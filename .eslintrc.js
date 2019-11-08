module.exports = {
  env: {
    es6: true,
    jest: true
  },
  extends: ["airbnb-base", "prettier"],
  plugins: ["prettier"],
  globals: {
    Atomics: "readonly",
    SharedArrayBuffer: "readonly"
  },
  parserOptions: {
    ecmaVersion: 2018,
    sourceType: "module"
  },
  rules: {
    "prettier/prettier": ["error"],
    "no-console": "off",
    "no-param-reassign": 0
  }
};
