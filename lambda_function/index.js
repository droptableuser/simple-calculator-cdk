console.log("Loading the calculator function");
var bucket = "calc-history";
var key =
  "calc_call_" +
  new Date().toISOString().replace(/:/g, "").replace(/\./, "") +
  ".txt";
exports.handler = function (event, context, callback) {
  console.log("Received event:", JSON.stringify(event, null, 2));

  var res = {};
  var method = event.httpMethod;
  if (method === "GET") {
    const pattern = /\d+\/\d+\/\S+/;
    var values = event.path.match(pattern);
    if (values) {
      res.operand1 = event.pathParameters.a;
      res.operand2 = event.pathParameters.b;
      res.operator = event.pathParameters.op;
    } else {
      callback(null, {
        statusCode: 400,
        body: "Invalid Path",
      });
    }
  }
  if (method === "POST") {
    values = JSON.parse(event.body);
    res.operand1 = Number(values.a);
    res.operand2 = Number(values.b);
    res.operator = values.op;
  }

  if (isNaN(res.operand1) || isNaN(res.operand2)) {
    callback(null, {
      statusCode: 400,
      body: "Invalid Operands",
    });
  }

  switch (res.operator) {
    case "=":
    case "add":
      res.result = res.operand1 + res.operand2;
      break;
    case "-":
    case "sub":
      res.result = res.operand1 - res.operand2;
      break;
    case "*":
    case "mul":
      res.result = res.operand1 * res.operand2;
      break;
    case "/":
    case "div":
      res.result =
        res.operand2 === 0 ? NaN : Number(res.operand1) / Number(res.operand2);
      break;
    default:
      callback(null, {
        statusCode: 400,
        body: "Invalid Operator",
      });
      break;
  }
  putObjectToS3(bucket, key, JSON.stringify(res));
  callback(null, {
    statusCode: 200,
    headers: {},
    body: JSON.stringify(res),
  });
};
var AWS = require("aws-sdk");
function putObjectToS3(bucket, key, data) {
  var s3 = new AWS.S3();
  var params = {
    Bucket: bucket,
    Key: key,
    Body: data,
  };
  s3.putObject(params, function (err, data) {
    if (err) console.log(err, err.stack);
    // an error occurred
    else console.log(data); // successful response
  });
}
