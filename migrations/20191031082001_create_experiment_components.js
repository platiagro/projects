
exports.up = function(knex) {
    return Promise.all([
        knex.schema.hasTable('experiment_components').then((exists) => {
            if(!exists) {
                return knex.schema.createTable('experiment_components', function(table) {
                    table.string('uuid', 255).primary();
                    table.dateTime('dateTime');
                    table.string('experimentId', 255)
                    .reference('uuid')
                    .inTable('experiments')
                    .notNull();
                    table.string('componentId', 255);
                    table.integer('position', 3);
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
