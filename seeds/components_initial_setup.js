/* eslint-disable func-names */
/* eslint-disable consistent-return */
exports.seed = function(knex) {
  return knex
    .select('*')
    .from('components')
    .then((rows) => {
      // Check if exists components
      if (rows && rows.length > 0) {
        return;
      }

      // Inserts seed entries
      return knex('components').insert([
        {
          uuid: 'b2935ec1-2146-41e4-a2c9-bbdc1400d267',
          createdAt: new Date(),
          name: 'AutoML',
          parameters:
            '[' +
            '{ "name": "automl_time_limit", "type": "int", "required": true }' +
            ']',
        },
        {
          uuid: 'cc6cd9ff-26c0-434e-a44e-531d510d695e',
          createdAt: new Date(),
          name: 'Criação de atributos por tempo',
          parameters:
            '[' +
            '{ "name": "feature_temporal_group", "type": "string", "required": true }, ' +
            '{ "name": "feature_temporal_period", "type": "string", "required": true }' +
            ']',
        },
        {
          uuid: '6a891e65-3547-4bd6-8681-1d04a514d8fd',
          createdAt: new Date(),
          name: 'Criação de atributos genéricos',
          parameters:
            '[' +
            '{ "name": "feature_tools_group", "type": "string", "required": true }' +
            ']',
        },
        {
          uuid: 'cd6faa74-5773-4d18-825b-986f011dd287',
          createdAt: new Date(),
          name: 'Filtro de atributos',
          parameters:
            '[' +
            '{ "name": "filter_columns", "type": "string", "required": true }' +
            ']',
        },
        {
          uuid: '8349b4a2-4d83-491a-a84d-9966e4558f1c',
          createdAt: new Date(),
          name: 'Pré-seleção de atributos',
          parameters:
            '[' +
            '{ "name": "preselection_1_na_cutoff", "type": "float", "required": true }, ' +
            '{ "name": "preselection_1_correlation_cutoff", "type": "float", "required": true }, ' +
            '{ "name": "preselection_2_na_cutoff", "type": "float", "required": true }, ' +
            '{ "name": "preselection_2_correlation_cutoff", "type": "float", "required": true }' +
            ']',
        },
        {
          uuid: 'ea0c33fe-bca1-4b25-a0fa-1dc13bec6c22',
          createdAt: new Date(),
          name: 'Regressão',
        },
      ]);
    });
};
