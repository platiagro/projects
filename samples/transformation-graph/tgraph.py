# -*- coding: utf-8 -*-
"""
Created on Nov 11 16:16:00 2019

@author: lladeira

Implementation based on the strategy proposed by https://udayankhurana.com/wp-content/uploads/2018/08/58.pdf
"""

import io
import os
import warnings
import random

import numpy as np
import pandas as pd
import networkx as nx

from sklearn.preprocessing import OrdinalEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score


class TGraph:

    def __init__(self,
                    data: pd.DataFrame,
                    feature_types: pd.DataFrame,
                    target_var: str,
                    group_var=None,
                    date_var=None,
                    budget=50):

        # Input variables
        self.data = data.dropna()
        self.feature_types = feature_types
        self.ftypes_list = feature_types[0].tolist()
        self.group_var = group_var
        self.date_name = date_var

        # Solution and methods parameters
        self.solution = data.copy()
        self.s_energy = 0

        # Initialize graph
        self.G = nx.DiGraph()
        self.node_indx = 1
        self.budget = budget
        self.nodes_ev = {}
        self.trans_ev = {}

        # Available transformations
        self.transformations = {"numeric" : ["sin", "cos", "tan", "square"],
                                "grouped": ["mean", "median", "std", "sum"],
                                "time": ["second", "minute", "hour", "day", "month", "year"]}

        # Separate variables
        self.target_name = target_var
        self.target_indx = list(self.solution.columns).index(target_var)
        self.target_type = self.feature_types[0].tolist()[self.target_indx]

        warnings.filterwarnings("ignore")

    def __name__(self):
        return 'TGraph'


    def preprocess(self):
        """
        Preprocess and create global variables.
        Parameters
        ----------
        Nothing
        Returns
        ----------
        Nothing
        """

        self.target = self.solution.pop(self.target_name).values
        self.ftypes_list.pop(self.target_indx)

        self.date = None
        if self.date_name is not None:
            date_indx = list(self.solution.columns).index(self.date_name)
            self.solution[self.date_name] = self.solution[self.date_name].astype(str)
            self.date = pd.to_datetime(self.solution.pop(self.date_name), infer_datetime_format=True)
            self.ftypes_list.pop(date_indx)

        # Encode all categorical and datetime features
        cat_feats_indexes = [indx for indx, x in enumerate(self.ftypes_list) if x != 'Numerical']
        if len(cat_feats_indexes) > 0:

            cat_feats = self.solution.columns[cat_feats_indexes].tolist()

            oe = OrdinalEncoder()

            if len(cat_feats) > 0:
                self.solution[cat_feats] = oe.fit_transform(self.solution[cat_feats])

        # Get numeric features
        num_feats_indexes = [indx for indx, x in enumerate(self.ftypes_list) if x == 'Numerical']
        self.num_feats = self.solution.columns[num_feats_indexes].tolist()

        # Add the 0 node to the graph
        reward = self.energy(self.solution)
        self.G.add_node(0, solution=self.solution,
                            cumulative=0,
                            reward=reward,
                            level=0,
                            trans_list=[])


    def cumulative_reward(self, ancestor_reward, node_reward, level):
        """
        Calculate cumulative reward.
        Parameters
        ----------
        ancestor_reward: float
            Reward calculated for the ancestor
        node_reward: float
            Reward calculated for the target node
        level: int
            Hight of the node
        Returns
        ----------
        cumulative_reward: float
            Cumulative reward calculated according to level and ancestor reward
        """

        discount = 1 - np.log(float(level)) / float(self.budget)

        return discount * node_reward + ancestor_reward


    def energy(self, solution, n_splits=10):
        """
        Calculate energy coeficient.
        In this case the energy refers to the algorithms f1-score (classification) or NMAE (regression).
        Parameters
        ----------
        solution: pandas.DataFrame
            Solution to calculate the energy
        n_splits: int
            Number of splits for kfold
        Returns
        ----------
        result_mean: float
            Mean result of kfold cross validation
        """

        solution = solution.fillna(method='ffill').fillna(method='bfill')

        # Machine Learning Parameters
        model, scoring = None, None

        if self.target_type == 'Categorical':
            model = RandomForestClassifier(random_state=0)
            scoring = 'f1_macro'
        else:
            model = RandomForestRegressor(random_state=0)
            scoring = 'neg_mean_absolute_error'

        # Kfold and obtain energy
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=0)
        results = cross_val_score(model, solution, self.target, cv=kf, scoring=scoring)

        return results.mean()


    def add_to_graph(self, ancestor_id, solution, trans):
        """
        Add a new node to the graph.
        Parameters
        ----------
        ancestor_id: int
            ID of ancestor node
        solution: pandas.DataFrame
            Solution to be added to the graph
        trans: str
            Transformation applied to the solution
        Returns
        ----------
        Nothing
        """

        # Evaluate solution
        reward = self.energy(solution)

        # Get cumulative reward
        cumulative = self.cumulative_reward(self.G.nodes[ancestor_id]['reward'], reward, self.G.nodes[ancestor_id]['level']+1)

        # Get improvement
        improvement = reward - self.G.nodes[ancestor_id]['reward']

        # Copy list of transformations from ancestor
        trans_list = self.G.nodes[ancestor_id]['trans_list'].copy()
        trans_list.append(trans)

        # Add new node
        self.G.add_node(self.node_indx, solution=solution,
                    cumulative=cumulative,
                    reward=reward,
                    improvement=improvement,
                    level=self.G.nodes[ancestor_id]['level']+1,
                    trans_list=trans_list)

        # Add edge conecting ancestor and new node
        self.G.add_edge(ancestor_id, self.node_indx, transformation=trans)

        ev = 0
        # Save state
        if self.config == 'reward':
            ev = reward
        elif self.config == 'cumulative':
            ev = cumulative
        else:
            ev = improvement

        self.nodes_ev[self.node_indx] = ev
        self.trans_ev[trans] = ev if trans not in self.trans_ev.keys() else (self.trans_ev[trans] + ev) / 2

        # Update next node id
        self.node_indx += 1


    def apply_numeric(self, solution, transformation):
        """
        Apply numeric transformation to all numeric columns.
        Parameters
        ----------
        solution: pandas.DataFrame
            A solution to be applied numeric transformations.
        transformation: str
            Transformation to be applied to the solution.
        Returns
        ----------
        Nothing
        """

        for column in self.num_feats:

            if column in list(solution.columns):

                np_func = getattr(np, transformation)

                # Create new column and fill with calculated value
                if '{0}---{1}'.format(transformation, column) not in list(solution.columns):
                    solution['{0}---{1}'.format(transformation, column)] = 0

                try:
                    solution['{0}---{1}'.format(transformation, column)] = solution[column].apply(lambda x: np_func(x))
                except:
                    solution.pop('{0}---{1}'.format(transformation, column))


    def apply_grouped(self, solution, transformation):
        """
        Apply grouped transformation to all numeric columns.
        Parameters
        ----------
        solution: pandas.DataFrame
            A solution to be applied numeric transformations.
        transformation: str
            Transformation to be applied to the solution.
        Returns
        ----------
        Nothing
        """

        if self.group_var is not None and len(self.group_var) > 0:

            for group_var in self.group_var:

                distinct_labels = self.solution[group_var].unique()

                for label in distinct_labels:

                    # Obtain which rows will be change according to label
                    labels_to_apply = solution[group_var] == label
                    filtered_by_label = solution.loc[labels_to_apply]

                    for column in self.num_feats:

                        if column not in self.group_var and column in list(solution.columns):

                            pd_func = getattr(pd.Series, transformation)

                            # Pandas doesnt deal well with spaces in query
                            if ' ' in group_var:
                                gv = group_var.replace(' ', '_')
                                solution = solution.rename(columns={group_var: gv})
                                group_var = gv

                            # Create new column and fill with calculated value
                            if '{0}---{1}---{2}'.format(group_var, transformation, column) not in list(solution.columns):
                                solution['{0}---{1}---{2}'.format(group_var, transformation, column)] = 0

                            try:
                                solution['{0}---{1}---{2}'.format(group_var, transformation, column)].loc[solution[group_var] == label] = pd_func(solution.query('%s == %s' % (group_var, label))[column])
                            except:
                                solution.pop('{0}---{1}---{2}'.format(group_var, transformation, column))

    def apply_timely(self, solution, transformation):
        """
        Apply timely transformation to all numeric columns.
        Parameters
        ----------
        solution: pandas.DataFrame
            A solution to be applied timely transformations.
        transformation: str
            Transformation to be applied to the solution.
        Returns
        ----------
        Nothing
        """

        if self.date is not None:

            new_feature = self.date.apply(lambda x : getattr(x, transformation))

            if len(np.unique(new_feature.tolist())) != 1:

                solution['{0}---{1}'.format(transformation, self.date.name)] = new_feature


    def apply_transformation(self, solution, transformation=None, trans_type=None):
        """
        Apply a transformation to a solution.
        Parameters
        ----------
        solution: pandas.DataFrame
            A solution to be applied transformations.
        transformation: str
            Transformation name
        trans_type: str
            Type of the transformation
        Returns
        ----------
        solution: pandas.DataFrame
            Generated solution
        """

        if trans_type == 'numeric':
            self.apply_numeric(solution, transformation)

        elif trans_type == 'grouped':
            self.apply_grouped(solution, transformation)

        elif trans_type == 'time':
            self.apply_timely(solution, transformation)

        return solution


    def init_transformations(self):
        """
        Initialize transformations and added all to the graph.
        Parameters
        ----------
        Nothing
        Returns
        ----------
        Nothing
        """

        for trans_type in ['numeric', 'grouped', 'time']:

            if trans_type == 'grouped' and (self.group_var is None or self.group_var not in list(self.G.nodes[0]['solution'].columns)):
                continue

            elif trans_type == 'time' and self.date_name is None:
                continue

            for trans in self.transformations[trans_type]:

                # Apply the transformation
                new_solution = self.apply_transformation(self.G.nodes[0]['solution'].copy(), trans, trans_type)

                # Add solution to graph
                self.add_to_graph(0, new_solution, trans)


    def search_best_node(self):
        """
        Create a new node considering past transformations.
        Parameters
        ----------
        Nothing
        Returns
        ----------
        best_node_id: int
            ID of the best node
        chosen_trans: str
            Transformation chosen to be applied
        """

        # Get the best node
        ordered_nodes = sorted(self.nodes_ev.items(), key=lambda value: value[1])
        best_node_id = ordered_nodes[-1][0]

        for i in range(len(ordered_nodes)-1, -1, -1):
            node_id = ordered_nodes[i][0]
            if self.G.nodes[node_id]['level'] <= len(list(self.trans_ev.keys())):
                best_node_id = node_id
                break

        best_node = self.G.nodes()[best_node_id]

        # Find best operation yet not used
        ordered_trans = sorted(self.trans_ev.items(), key=lambda value: value[1])

        chosen_trans = None

        for i in range(len(ordered_trans)-1, -1, -1):
            if ordered_trans[i][0] not in best_node['trans_list']:
                chosen_trans = ordered_trans[i][0]
                break

        return best_node_id, chosen_trans


    def fill_template(self, trans_applied, column):

        trans = column.split('---')[0]
        col_name = column.split('---')[1]

        if trans not in self.transformations['grouped']:
            trans_applied[column] = ''

        else:

            group_var = column.split('---')[2]
            labels = list(self.solution[group_var].unique())

            trans_grouped = {}
            for x in range(len(labels)):
                label_index = self.solution[self.solution[group_var] == labels[x]].iloc[0].name
                value = self.solution[self.solution[group_var] == labels[x]].iloc[0][column]
                trans_grouped[str(self.data.iloc[label_index][group_var])] = value

            trans_applied[column] = trans_grouped


    def format_output(self):
        """
        Format output to make bestsolution look like data.
        Parameters
        ----------
        Nothing
        Returns
        ----------
        data: pandas.DataFrame
            Formated data result
        """

        trans_applied = {}

        for column in list(self.solution.columns):

            if column not in list(self.data.columns):

                self.data[column] = self.solution[column]
                new_line = pd.DataFrame({0: 'Numerical'}, index=[self.feature_types.shape[0]])
                self.feature_types = pd.concat([self.feature_types, new_line])

                self.fill_template(trans_applied, column)

        return self.data, self.feature_types, trans_applied


    def auto_feat(self, config='reward'):
        """
        Executes auto featuring.
        Parameters
        ----------
        Nothing
        Returns
        ----------
        data: pandas.DataFrame
            Data result
        feature_types: pd.DataFrame
            All feature types
        trans_applied: dict
            Transformations applied in the data
        """

        self.config = config

        self.init_transformations()

        try:

            while (self.budget > self.node_indx):

                node_id, trans = self.search_best_node()

                trans_type = None

                if trans in self.transformations['numeric']:
                    trans_type = 'numeric'
                elif trans in self.transformations['grouped']:
                    trans_type = 'grouped'
                elif trans in self.transformations['time']:
                    trans_type = 'time'

                # Apply the transformation
                new_solution = self.apply_transformation(self.G.nodes[node_id]['solution'].copy(), trans, trans_type)

                # Add solution to graph
                self.add_to_graph(node_id, new_solution, trans)

        except:
            pass

        # Get final result
        node_id, trans = self.search_best_node()
        self.solution = self.G.nodes[node_id]['solution']

        return self.format_output()
