require('dotenv').config();

const password = process.env.DB_ROOT_PASSWORD || 'secret';
const database = process.env.DB_DATABASE || 'projects';
const host = process.env.DB_HOST || 'mysql';
const port = process.env.DB_PORT || 3306;

const testPassword = process.env.DB_TEST_ROOT_PASSWORD || 'secret';
const testDatabase = process.env.DB_TEST_DATABASE || 'projects';
const testHost = process.env.DB_TEST_HOST || 'mysql';
const testPort = process.env.DB_TEST_PORT || 3306;

const config = {
  client: 'mysql',
  connection: {
    user: 'root',
    password,
    host,
    port,
    database,
  },
};

const testConfig = {
  client: 'mysql',
  connection: {
    user: 'root',
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
