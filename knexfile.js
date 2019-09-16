const user = process.env.DB_USER;
const password = process.env.DB_PASSWORD;
const database = process.env.DB_DATABASE;
const host = process.env.DB_HOST;
const port = process.env.DB_PORT;

const testUser = process.env.DB_TEST_USER;
const testPassword = process.env.DB_TEST_PASSWORD;
const testDatabase = process.env.DB_TEST_DATABASE;
const testHost = process.env.DB_TEST_HOST;
const testPort = process.env.DB_TEST_PORT;

const config = {
  client: 'mysql',
  connection: {
    user,
    password,
    host,
    port,
    database,
  },
};

const testConfig = {
  client: 'mysql',
  connection: {
    user: testUser,
    password: testPassword,
    database: testDatabase,
    host: testHost,
    port: testPort,
  },
};

module.exports.staging = config;
module.exports.development = config;
module.exports.production = config;
module.exports.config = config;
module.exports.test = testConfig;
