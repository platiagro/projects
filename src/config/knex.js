import 'dotenv/config';
import knexfile from '../../knexfile';

const env = process.env.NODE_ENV || 'development';
const knex = require('knex')(knexfile[env]);

export default knex;
