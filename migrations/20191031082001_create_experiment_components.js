
exports.up = function(knex) {
    return Promise.all([
        knex.schema.hasTable('experiment_components').then((exists) => {
            if(!exists) {
                return knex.schema.createTable('experiment_components', function(table) {
                    table.string('uuid', 255).primary();
                    table.dateTime('dateTime')
                    .notNull();
                    table.string('experimentId', 255)
                    .references('uuid')
                    .inTable('experiments')
                    .notNull();
                    table.string('componentId', 255)
                    .notNull();
                    table.integer('position', 3)
                    .notNull();
                });
            }
        })
  ]);
};

exports.down = function(knex) {
    return Promise.all([
        knex.schema.
        dropTable('experiment_component')
    ]);
};
