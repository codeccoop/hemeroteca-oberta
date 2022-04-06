const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {
  entry: "./src/index.js",
  output: {
    filename: "main.js",
    path: path.resolve(__dirname, "dist"),
    clean: true
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env"]
          }
        }
      },
      {
        test: /\.s?css$/i,
        use: [
          "style-loader",
          "css-loader",
          "sass-loader",
          {
            loader: "postcss-loader",
            options: {
              postcssOptions: {
                plugins: [
                  process.env.NODE_ENV === "production"
                    ? [
                        "postcss-preset-env",
                        "autoprefixer",
                        "cssnano",
                        {
                          // Options
                        }
                      ]
                    : ["postcss-preset-env", "autoprefixer"]
                ]
              }
            }
          }
        ]
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      title: "Hemeroteca Oberta",
      template: "index.html",
      minify: true,
      base: process.env.NODE_ENV === "production" ? "/hemerotecaoberta/" : null
    }),
    new CopyPlugin({
      patterns: [{ from: "public", to: "dist" }]
    })
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, "public")
    },
    port: 9000,
    host: "127.0.0.1",
    liveReload: true
  }
};
