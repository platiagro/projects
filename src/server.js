import { Config } from './config';
import app from './app';

const port = Config.PORT;
app.listen(port, () => {
  console.log(`API running on port ${port}!`);
});
