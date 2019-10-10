/* eslint-disable func-names */
/* eslint-disable consistent-return */
exports.up = function(knex) {
  return Promise.all([
    knex.schema.hasTable('projects').then((exists) => {
      if (!exists) {
        return knex.schema.createTable('projects', function(t) {
          t.string('uuid', 255).primary();
          t.string('name', 255).notNull();
          t.dateTime('createdAt').notNull();
        });
      }
    }),
    knex.schema.hasTable('experiments').then((exists) => {
      if (!exists) {
        return knex.schema.createTable('experiments', function(t) {
          t.string('uuid', 255).primary();
          t.string('name', 255).notNull();
          t.string('projectId', 255)
            .references('uuid')
            .inTable('projects')
            .notNull();
          t.string('pipelineIdTrain', 255).nullable();
          t.string('pipelineIdDeploy', 255).nullable();
          t.string('datasetId', 255).nullable();
          t.string('headerId', 255).nullable();
          t.string('targetColumnId', 255).nullable();
          t.text('parameters', 'longtext').nullable();
          t.dateTime('createdAt').notNull();
          t.integer('position', '3').nullable();
        });
      }
    }),

    knex.schema.hasTable('pipelines').then((exists) => {
      if (!exists) {
        return knex.schema.createTable('pipelines', function(t) {
          t.string('uuid', 255).primary();
        });
      }
    }),

    knex.schema.hasTable('datasets').then((exists) => {
      if (!exists) {
        return knex.schema.createTable('datasets', function(t) {
          t.string('uuid', 255).primary();
          t.string('bucketName', 255).notNull();
          t.string('originalName', 255).notNull();
        });
      }
    }),

    knex.schema.hasTable('headers').then((exists) => {
      if (!exists) {
        return knex.schema.createTable('headers', function(t) {
          t.string('uuid', 255).primary();
          t.string('bucketName', 255).notNull();
          t.string('originalName', 255).notNull();
        });
      }
    }),

    knex.schema.hasTable('columns').then((exists) => {
      if (!exists) {
        return knex.schema.createTable('columns', function(t) {
          t.string('uuid', 255).primary();
          t.string('headerId', 255)
            .references('uuid')
            .inTable('headers')
            .notNull();
          t.string('name', 255).notNull();
          t.string('datatype', 255).notNull();
          t.integer('position', 5).notNull();
        });
      }
    }),
  ]);
};

exports.down = function(knex) {
  return Promise.all([
    knex.schema.dropTable('columns'),
    knex.schema.dropTable('headers'),
    knex.schema.dropTable('datasets'),
    knex.schema.dropTable('pipelines'),
    knex.schema.dropTable('experiments'),
    knex.schema.dropTable('projects'),
  ]);
};
