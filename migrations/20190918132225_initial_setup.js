exports.up = function(knex) {
  return Promise.all([
    knex.schema.createTable('projects', function(t) {
      t.string('uuid', 255).primary();
      t.string('name', 255).notNull();
      t.dateTime('createdAt').notNull();
    }),

    knex.schema.createTable('experiments', function(t) {
      t.string('uuid', 255).primary();
      t.string('name', 255).notNull();
      t.string('projectId', 255)
        .references('uuid')
        .inTable('projects')
        .notNull();
      t.string('pipelineId', 255).nullable();
      t.string('datasetId', 255).nullable();
      t.string('targetColumnId', 255).nullable();
      t.text('parameters', 'longtext').nullable();
      t.dateTime('createdAt').notNull();
    }),

    knex.schema.createTable('pipelines', function(t) {
      t.string('uuid', 255).primary();
    }),

    knex.schema.createTable('datasets', function(t) {
      t.string('uuid', 255).primary();
    }),

    knex.schema.createTable('columns', function(t) {
      t.string('uuid', 255).primary();
      t.string('datasetId', 255)
        .references('uuid')
        .inTable('datasets')
        .notNull();
      t.string('dataType').notNull();
    }),
  ]);
};

exports.down = function(knex) {
  return Promise.all([
    knex.schema.dropTable('columns'),
    knex.schema.dropTable('datasets'),
    knex.schema.dropTable('pipelines'),
    knex.schema.dropTable('experiments'),
    knex.schema.dropTable('projects'),
  ]);
};
