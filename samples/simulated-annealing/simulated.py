# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 09:04:00 2019

@author: lladeira
"""

import io
import os
import sys
import warnings
import random
from random import gauss
import multiprocessing
from multiprocessing import Process
from multiprocessing import Manager
import threading

import numpy as np
import pandas as pd
import networkx as nx

from sklearn.preprocessing import OrdinalEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score

from scipy import constants


class SimulatedAnnealing:

    ## Contants
    # Update Temperature

    def __init__(self,
                    data: pd.DataFrame,
                    feature_types: pd.DataFrame,
                    target_var: str,
                    group_var=None,
                    date_var=None,
                    alpha=1.0):

        # Input variables
        self.data = data.dropna()
        self.feature_types = feature_types
        self.ftypes_list = feature_types[0].tolist()
        self.group_var = group_var
        self.date_name = date_var

        # Configure temperature
        quantity_records = np.round((100/(np.log(data.shape[0])))*3)
        quantity_features = np.round(100/np.log(data.shape[1]))

        self.temperature = quantity_records * quantity_features * alpha

        # Rank - transformation graph
        self.G = nx.Graph()

        # Solution and methods parameters
        self.best_solution = self.data.copy()
        self.best_solution_energy = 0

        # Available transformations
        self.transformations = {"numeric" : ["sin", "cos", "tan", "square"],
                                "grouped": ["mean", "median", "std", "sum"],
                                "time": ["second", "minute", "hour", "day", "month", "year", 'dayofweek']}

        # Separate variables
        self.target_name = target_var
        self.target_indx = list(self.data.columns).index(target_var)
        self.target_type = self.ftypes_list[self.target_indx]

        warnings.filterwarnings("ignore")

        # Parallel processing
        self.lock = threading.Lock()


    def __name__(self):
        return 'SimulatedAnnealing'


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

        # Remove variables
        self.target_var = self.best_solution.pop(self.target_name).values
        self.ftypes_list.pop(self.target_indx)

        if self.date_name is not None:
            date_indx = list(self.best_solution.columns).index(self.date_name)
            self.best_solution[self.date_name] = self.best_solution[self.date_name].astype(str)
            self.date_var = pd.to_datetime(self.best_solution.pop(self.date_name), infer_datetime_format=True)
            self.ftypes_list.pop(date_indx)

        # Convert all categorical columns to numerical
        cat_feats_indexes = [indx for indx, x in enumerate(self.ftypes_list) if x != 'Numerical']
        if len(cat_feats_indexes) > 0:

            cat_feats = self.best_solution.columns[cat_feats_indexes].tolist()

            oe = OrdinalEncoder()

            if len(cat_feats) > 0:
                self.best_solution[cat_feats] = oe.fit_transform(self.best_solution[cat_feats])

        # Get numeric columns
        num_feats_indexes = [indx for indx, x in enumerate(self.ftypes_list) if x == 'Numerical']
        self.num_feats =  self.best_solution.columns[num_feats_indexes].tolist()

        # Copy to initiate every round
        self.data_processed = self.best_solution.copy()

        # Generate transformation graph
        self.generate_t_graph()


    def generate_t_graph(self):
        """
        Generate a transformation graph to store the good relationships.
        Parameters
        ----------
        Nothing
        Returns
        ----------
        Nothing
        """

        for trans_types in self.transformations:
            for trans in self.transformations[trans_types]:
                self.G.add_node(trans)


    def get_weights(self, trans):
        """
        Get a list of transformations and count the neighbors.
        Parameters
        ----------
        trans: list
            The list of transformations.
        Returns
        ----------
        weight_list: list
            List of weights (neighbors) for each transformation.
        """

        weight_list = []

        for t in trans:
            weight = len(list(self.G.neighbors(t)))

            if weight == 0:
                weight = 1

            weight_list.append(weight)

        return weight_list


    def parse_weight(self, weight_list):
        """
        Parse weight to a percentage with sum 1.
        Parameters
        ----------
        weight_list: list
            The weight list.
        Returns
        ----------
        weight_list: list
            Also the weight list.
        """
        weight = sum(weight_list)

        return list(map(lambda x: x/weight, weight_list))


    def apply_numeric(self, new_solution):
        """
        Apply numeric transformations to all numeric columns.
        Parameters
        ----------
        new_solution: pandas.DataFrame
            A solution to be applied numeric transformations.
        percentage: float
            The percentage of features to be applied.
        Returns
        ----------
        numbt: list
            List of transformations applied.
        """

        if len(self.num_feats) > 0:

            # Get a percentage based on gaussian
            percentage = gauss(0.8, 0.3)

            # Put a superior limit
            if percentage > 1.0:
                percentage = 1.0

            # Put a inferior limit
            if percentage < 0.0:
                percentage = 0.1

            qt_trans = int(np.ceil(percentage*len(self.transformations["numeric"])))

            if qt_trans == 0:
                qt_trans = 1

            weight_list = self.get_weights(self.transformations["numeric"])

            numbt = list(np.random.choice(self.transformations["numeric"], size=qt_trans, replace=False, p=self.parse_weight(weight_list)))

            for column in self.num_feats:

                if column in list(new_solution.columns):

                    for numb in numbt:

                        np_func = getattr(np, numb)

                        # Create new column and fill with calculated value
                        if '{0}---{1}'.format(numb, column) not in list(new_solution.columns):
                            new_solution['{0}---{1}'.format(numb, column)] = 0

                        try:
                            new_solution['{0}---{1}'.format(numb, column)] = new_solution[column].apply(lambda x: np_func(x))
                        except:
                            new_solution.pop('{0}---{1}'.format(numb, column))

            return numbt


    def apply_grouped(self, new_solution):
        """
        Apply grouped transformations to all numeric columns.
        Parameters
        ----------
        new_solution: pandas.DataFrame
            A solution to be applied grouped numeric transformations.
        percentage: float
            The percentage of features to be applied.
        Returns
        ----------
        groupt: list
            List of transformations applied.
        """

        if self.group_var is not None and len(self.group_var) > 0:

            # Get a percentage based on gaussian
            percentage = gauss(0.8, 0.3)

            # Put a superior limit
            if percentage > 1.0:
                percentage = 1.0

            # Put a inferior limit
            if percentage < 0.0:
                percentage = 0.1

            qt_trans = int(np.ceil(percentage*len(self.transformations["grouped"])))

            if qt_trans == 0:
                qt_trans = 1

            weight_list = self.get_weights(self.transformations["grouped"])

            groupt = list(np.random.choice(self.transformations["grouped"], size=qt_trans, replace=False, p=self.parse_weight(weight_list)))

            for group_var in self.group_var:

                distinct_labels = self.best_solution[group_var].unique()

                for label in distinct_labels:

                    # Obtain which rows will be change according to label
                    labels_to_apply = new_solution[group_var] == label
                    filtered_by_label = new_solution.loc[labels_to_apply]

                    for column in self.num_feats:

                        if column not in self.group_var and column in list(new_solution.columns):

                            for group in groupt:

                                pd_func = getattr(pd.Series, group)

                                # Pandas doesnt deal well with spaces in query
                                if ' ' in group_var:
                                    gv = group_var.replace(' ', '_')
                                    new_solution = new_solution.rename(columns={group_var: gv})
                                    group_var = gv

                                # Create new column and fill with calculated value
                                if '{0}---{1}---{2}'.format(group_var, group, column) not in list(new_solution.columns):
                                    new_solution['{0}---{1}---{2}'.format(group_var, group, column)] = 0

                                try:
                                    new_solution['{0}---{1}---{2}'.format(group_var, group, column)].loc[new_solution[group_var] == label] = pd_func(new_solution.query('%s == %s' % (group_var, label))[column])
                                except:
                                    new_solution.pop('{0}---{1}---{2}'.format(group_var, group, column))

            return groupt


    def apply_timely(self, new_solution):
        """
        Apply timely transformations to all time columns
        Parameters
        ----------
        new_solution: pandas.DataFrame
            A solution to be applied timely transformations.
        percentage: float
            The percentage of features to be applied.
        Returns
        ----------
        timet: list
            List of transformations applied.
        """

        if self.date_name is not None:

            # Get a percentage based on gaussian
            percentage = gauss(0.8, 0.3)

            # Put a superior limit
            if percentage > 1.0:
                percentage = 1.0

            # Put a inferior limit
            if percentage < 0.0:
                percentage = 0.1

            qt_trans = int(np.ceil(percentage*len(self.transformations["time"])))

            if qt_trans == 0:
                qt_trans = 1

            weight_list = self.get_weights(self.transformations["time"])

            timet = list(np.random.choice(self.transformations["time"], size=qt_trans, replace=False, p=self.parse_weight(weight_list)))

            for time in timet:

                if time == 'dayofweek':
                    new_feature = self.date_var.dt.dayofweek
                else:
                    new_feature = self.date_var.apply(lambda x : getattr(x, time))

                if len(np.unique(new_feature.tolist())) != 1:

                    new_solution['{0}---{1}'.format(time, self.date_name)] = new_feature

            return timet


    def move(self):
        """
        Generate new solution.
        Parameters
        ----------
        Nothing
        Returns
        ----------
        new_solution: pandas.DataFrame
            Generated solution
        numbt: list
            List of numeric features applied
        groupt: list
            List of grouped features applied
        timet: list
            List of timely features applied
        """

        new_solution = self.data_processed.copy()
        # new_solution = self.select_features(new_solution)

        numbt, groupt, timet = [], [], []

        # If it's numeric than choose a numeric transformation
        if len(self.transformations['numeric']) > 0:
            numbt = self.apply_numeric(new_solution)

        # If it's numeric than choose a numeric transformation and group it
        if len(self.transformations['grouped']) > 0:
            groupt = self.apply_grouped(new_solution)

        # If it's timestamp than choose a timely transformation
        if len(self.transformations['time']) > 0:
            timet = self.apply_timely(new_solution)

        return new_solution, numbt, groupt, timet


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
        results = cross_val_score(model, solution, self.target_var, cv=kf, scoring=scoring)

        return results.mean()


    def do_i_switch(self, bs_energy, ns_energy):
        """
        Verify if it's acceptable to switch to a worst solution.
        http://www.cs.cmu.edu/afs/cs.cmu.edu/project/learn-43/lib/photoz/.g/web/glossary/anneal.html
        Parameters
        ----------
        bs_energy: float
            Energy of best solution
        ns_energy: float
            Energy of new solution
        Returns
        ----------
        res: boolean
            True if it have to change or False if it does not have
        """

        # Calculate how worse it is
        if ns_energy < 0:
            bs_energy = -bs_energy
            ns_energy = -ns_energy

            aux = bs_energy
            bs_energy = ns_energy
            ns_energy = aux

        x = ns_energy / bs_energy
        delta_e = (1 - x) * 100

        # Calculate the switch probability
        switch_prob = np.exp(-delta_e / self.temperature)

        # Verify if it's in the range
        if random.random() < switch_prob:
            return True
        return False


    def uptemp_boltzman(self):
        """
        Update temperature according to boltzman.
        Amazingly just the square root.
        https://www.mathworks.com/help/gads/how-simulated-annealing-works.html
        Parameters
        ----------
        Nothing
        Returns
        ----------
        Nothing
        """
        self.temperature -= np.sqrt(self.temperature)


    def add_edges_graph(self, numbt, groupt, timet):
        """
        Add edges to transformation's graph.
        Parameters
        ----------
        numbt: list
            List of numeric features applied
        groupt: list
            List of grouped features applied
        timet: list
            List of timely features applied
        Returns
        ----------
        Nothing
        """

        # Put all transformations in a list
        trans = []

        if numbt is not None:

            for n in numbt:
                trans.append(n)

        if groupt is not None:

            for g in groupt:
                trans.append(g)

        if timet is not None:

            for t in timet:
                trans.append(t)

        # Create edges between all of them
        if len(trans) > 0:

            for i in range(len(trans)-1):

                for j in range(i+1, len(trans)):

                    try:
                        self.G.add_edge(trans[i], trans[j], weight=5)
                    except:
                        self.G[trans[i]][trans[j]]['weight'] += 1


    def remove_edges_graph(self, numbt, groupt, timet):
        """
        Remove edges to transformation's graph.
        Parameters
        ----------
        numbt: list
            List of numeric features applied
        groupt: list
            List of grouped features applied
        timet: list
            List of timely features applied
        Returns
        ----------
        Nothing
        """

        # Put all transformations in a list
        trans = []

        if numbt is not None:

            for n in numbt:
                trans.append(n)

        if groupt is not None:

            for g in groupt:
                trans.append(g)

        if timet is not None:

            for t in timet:
                trans.append(t)

        # Remove edges between all of them
        if len(trans) > 0:

            for i in range(len(trans)-1):

                for j in range(i+1, len(trans)):

                    if self.G.get_edge_data(trans[i], trans[j]) != None:
                        if self.G.get_edge_data(trans[i], trans[j])['weight'] > 1:
                            self.G[trans[i]][trans[j]]['weight'] -= 1
                        else:
                            self.G.remove_edge(trans[i], trans[j])


    def parallel_feat(self, iterate, solutions):
        """
        Parallel auto_feat by calling a number of processes.
        Parameters
        ----------
        iterate: int
            ID of thread (0-cpu count)
        solutions: multiprocessing.Manager().dict()
            Manageable dictionary to save results
        Returns
        ----------
        Nothing
        """

        # Generates new solution
        new_solution, numbt, groupt, timet = self.move()
        ns_energy = float(self.energy(new_solution.copy()))

        if  ns_energy > self.best_solution_energy:
            solutions[str(iterate)] = {'ns': new_solution,
                                        'nse': ns_energy,
                                        'calc': ns_energy,
                                        'numbt': numbt,
                                        'groupt': groupt,
                                        'timet': timet}

        elif self.do_i_switch(self.best_solution_energy, ns_energy):
            solutions[str(iterate)] = {'ns': new_solution,
                                        'nse': ns_energy,
                                        'calc': ns_energy,
                                        'numbt': numbt,
                                        'groupt': groupt,
                                        'timet': timet}
        else:
            solutions[str(iterate)] = {'ns': new_solution,
                                        'nse': None,
                                        'calc': ns_energy,
                                        'numbt': numbt,
                                        'groupt': groupt,
                                        'timet': timet}

        return solutions


    def update_solution(self, solutions):
        """
        Update the best solution according to the solutions obtained
        Parameters
        ----------
        solutions: multiprocessing.Manager.dict()
            Solutions obtained
        Returns
        ----------
        Nothing
        """

        higher_solution = None
        higher_energy = -sys.maxsize

        # Go through all solutions
        for i, s in enumerate(solutions):

            sol = solutions[s]

            # Verify if solution is tradable
            if sol['nse'] != None:

                # Add a new edge or improve weight
                self.add_edges_graph(sol['numbt'],
                                sol['groupt'],
                                sol['timet'])

                if sol['nse'] > higher_energy:
                    higher_solution = sol['ns']
                    higher_energy = sol['nse']

            # If it is not tradable remove edge
            else:
                self.remove_edges_graph(sol['numbt'],
                                sol['groupt'],
                                sol['timet'])

        if higher_energy != -sys.maxsize:
            self.best_solution = higher_solution
            self.best_solution_energy = higher_energy


    def fill_template(self, trans_applied, column):
        """
        Create a template with all operations applied.
        Parameters
        ----------
        data: pd.DataFrame
            Initial data
        best_solution: pd.DataFrame
            Best solution found
        trans_applied: dict
            Transformation applied in order
        columns: str
            Referred column
        Returns
        ----------
        Nothing
        """

        trans = column.split('---')[0]
        col_name = column.split('---')[1]

        if trans not in self.transformations['grouped']:
            trans_applied[column] = ''

        else:

            group_var = column.split('---')[2]
            labels = list(self.best_solution[group_var].unique())

            trans_grouped = {}
            for x in range(len(labels)):
                label_index = self.best_solution[self.best_solution[group_var] == labels[x]].iloc[0].name
                value = self.best_solution[self.best_solution[group_var] == labels[x]].iloc[0][column]
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
        feature_types: pd.DataFrame
            All feature types
        trans_applied: dict
            Transformations applied in the data
        """

        trans_applied = {}

        for column in list(self.best_solution.columns):

            if column not in list(self.data.columns):

                self.data[column] = self.best_solution[column]
                new_line = pd.DataFrame({0: 'Numerical'}, index=[self.feature_types.shape[0]])
                self.feature_types = pd.concat([self.feature_types, new_line])

                self.fill_template(trans_applied, column)

        return self.data, self.feature_types, trans_applied


    def auto_feat(self):
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

        if len(self.num_feats) == 0 and self.date_name is None:
            return self.data, self.feature_types, {}

        # Calculate energy of first solution
        self.best_solution_energy = self.energy(self.best_solution.copy())
        default_energy = self.best_solution_energy

        try:

            # Iterates temperature
            while(self.temperature > 0):

                manager = Manager()
                solutions = manager.dict()

                processes = [Process(target=self.parallel_feat, args=(iterate, solutions)) for iterate in range(multiprocessing.cpu_count()//2)]

                # Run processes
                for p in processes:
                    p.start()

                # Exit the completed processes
                for p in processes:
                    p.join()

                    self.uptemp_boltzman()

                self.update_solution(solutions)

        except:
            pass

        if self.energy(self.best_solution.copy()) < default_energy:
            self.best_solution = self.data

        return self.format_output()
