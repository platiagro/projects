# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 08:05:00 2019

@author: ascalet / lladeira

Feature Tools implementation utilizing feature tools Data Science Machine
"""

import io
import os

import numpy as np
import pandas as pd
import warnings

import featuretools as ft
import featuretools.variable_types as vtypes


class FeatureTools():


    def __init__(self,
                    data: pd.DataFrame,
                    feature_types: pd.DataFrame,
                    target_var: str,
                    group_var=None,
                    date_var=None,
                    names='id'):

        self.data = data.dropna()
        self.feature_types = feature_types
        self.group_var = group_var
        self.date_var = date_var
        self.names = names

        if date_var is not None:
            self.data[date_var] = pd.to_datetime(self.data[date_var])

        warnings.filterwarnings("ignore")


    def __name__(self):
        return 'FeatureTools'


    def parse_data(self):
        """
        Parse data from dataframe to EntitySet (FeatureTools formatting)
        Parameters
        ----------
        Nothing
        Returns
        ----------
        es: EntitySet
            The entity set of grouped data.
        """

        es = ft.EntitySet(id="Dados")

        columns = list(self.data.columns)
        variable_types = {}

        for indx, ftype in enumerate(self.feature_types[0].values):

            if ftype == 'Categorical':
                variable_types[columns[indx]] = vtypes.Categorical

        # Create EntitySet and load data
        es = es.entity_from_dataframe(entity_id="entity", dataframe=self.data,
                                    make_index=True, index=self.names,
                                    time_index=self.date_var, variable_types=variable_types)

        # Groups data if required
        # Commented because variable grouped doesn't exist on dataset
        es.normalize_entity(new_entity_id="normal", base_entity_id="entity", index=self.group_var[0])

        return es


    def add_feature_types(self, result):
        """
        Add new feature types according to created columns
        Parameters
        ----------
        result: pd.DataFrame
            The resulting data with old and new columns
        Returns
        ----------
        Nothing
        """

        df_indx = self.feature_types.shape[0]
        qtd = len(list(result.columns)) - df_indx

        for indx in range(qtd):
            new_line = pd.DataFrame({0: 'Numerical'}, index=[df_indx+indx])
            self.feature_types = pd.concat([self.feature_types, new_line])


    def create_feat_template(self, data, result):
        """
        Create feature template so that it may be recreated in the implementation
        Parameters
        ----------
        data: pd.DataFrame
            Data input
        result: pd.DataFrame
            The resulting data with old and new columns
        Returns
        ----------
        trans_applied: dict
            Transformations applied by the feature tools algorithm
        """

        trans_applied = {}
        gv = self.group_var[0]

        for column in list(result.columns):

            if column not in list(self.data.columns):

                if 'first_entity_time' in column or 'normal' not in column:

                    trans = column.split('(')[0].lower()
                    col = column.split('(')[1].replace(')', '')

                    if '.' in trans:
                        trans = trans.split('.')[1]

                    trans_applied['%s---%s' % (trans, col)] = ""

                else:

                    # Remove unsuned names
                    col_aux = column.split('.')[1:]

                    trans = col_aux[0].split('(')[0].lower()
                    col = col_aux[1].replace(')', '')

                    labels = list(result[gv].unique())

                    trans_grouped = {}
                    for x in range(len(labels)):

                        label_index = result.query("%s == '%s'" % (gv, labels[x])).iloc[0].name

                        value = result.query("%s == '%s'" % (gv, labels[x])).iloc[0][column]

                        trans_grouped[str(data.iloc[label_index][gv])] = float(value)

                    trans_applied['%s---%s---%s' % (trans, col, gv)] = trans_grouped

        return trans_applied


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

        if self.group_var == None or len(self.group_var) == 0:
            return self.data, self.feature_types, {}

        # Parse data dataframe to EntitySet
        es = self.parse_data()

        # Get the amplitude of data
        def amplitude(values):
            amp=values.max()-values.min()
            return amp

        amplitude = ft.primitives.make_agg_primitive(amplitude, input_types=[ft.variable_types.Numeric],
                                                       return_type=ft.variable_types.Numeric, name="amplitude",
                                                       description="Calcula a amplitude geral de cada variável numérica",
                                                       cls_attributes=None, uses_calc_time=False, commutative=False, number_output_features=1)

        # Generate aggregated primitives
        ft_matrix1, relationships1 = ft.dfs(entityset=es, target_entity="entity",
                                        agg_primitives=[amplitude, "avg_time_between",
                                                        "mean","median", "std", "sum"],
                                        verbose=True)
        # Generate transformation primitives
        ft_matrix2, relationships2 = ft.dfs(entityset=es, target_entity="entity",
                                        trans_primitives=["second", "minute", "hour",
                                                        "day", "month", "year",
                                                        "weekday"],
                                        verbose=True, max_depth=1)

         # Concatenate the results and remove duplicated columns
        features = pd.concat([self.data, ft_matrix1, ft_matrix2], axis=1, copy=False)
        result = features.loc[:, ~features.columns.duplicated()].dropna()

        # Remove unused columns
        cols = [c for c in result.columns if 'first_entity_time' not in c]
        result = result[cols]

        if 'id' in list(result.columns):
            result.drop("id", axis=1, inplace=True)

        self.add_feature_types(result)

        trans_applied = self.create_feat_template(self.data, result)

        return result, self.feature_types, trans_applied
