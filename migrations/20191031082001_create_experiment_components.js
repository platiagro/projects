exports.up = function(knex) {
  return Promise.all([
    knex.schema.hasTable('experiment_components').then((exists) => {
      if (!exists) {
        return knex.schema.createTable('experiment_components', function(t) {
          t.string('uuid', 255).primary();
          t.dateTime('createdAt').notNull();
          t.string('experimentId', 255)
            .references('uuid')
            .inTable('experiments')
            .notNull();
          t.string('componentId', 255).notNull();
          t.integer('position', 3).notNull();
        });
      }
      return null;
    }),
  ]);
};

exports.down = function(knex) {
  return Promise.all([knex.schema.dropTable('experiment_component')]);
};
