var virtualPins = [
  [
    "V0",
    "0"
  ],
  [
    "V1",
    "1"
  ],
  [
    "V2",
    "2"
  ],
  [
    "V3",
    "3"
  ],
  [
    "V4",
    "4"
  ],
  [
    "V5",
    "5"
  ],
  [
    "V6",
    "6"
  ],
  [
    "V7",
    "7"
  ],
  [
    "V8",
    "8"
  ],
  [
    "V9",
    "9"
  ],
  [
    "V10",
    "10"
  ],
  [
    "V11",
    "11"
  ],
  [
    "V12",
    "12"
  ],
  [
    "V13",
    "13"
  ],
  [
    "V14",
    "14"
  ],
  [
    "V15",
    "15"
  ],
  [
    "V16",
    "16"
  ],
  [
    "V17",
    "17"
  ],
  [
    "V18",
    "18"
  ],
  [
    "V19",
    "19"
  ],
  [
    "V20",
    "20"
  ]
];

Blockly.Blocks["era_mqtt_connect"] = {
  init: function () {
    this.jsonInit({
      colour: "#ff8d12",
      nextStatement: null,
      tooltip: "Kết nối đến server Era",
      message0: "kết nối Era với WiFi %1 password %2 %3 token %4",
      previousStatement: null,
      args0: [
        {
          "type": "field_input",
          "name": "WIFI",
          "text": "ssid"
        },
        {
          "type": "field_input",
          "name": "PASSWORD",
          "text": "password"
        },
        {
          "type": "input_dummy"
        },
        {
          "type": "field_input",
          "name": "TOKEN",
          "text": "xxxxxxx-yyyy-xxxx-yyyy-xxxxxxxxxxxx"
        }
      ],
      helpUrl: "",
    });
  },
};

Blockly.Python['era_mqtt_connect'] = function(block) {
  var wifi = block.getFieldValue('WIFI');
  var password = block.getFieldValue('PASSWORD');
  var token = block.getFieldValue('TOKEN');

  Blockly.Python.definitions_['import_era_iot'] = 'from era_iot import *';
  Blockly.Python.definitions_['init_era_mqtt'] = "era_iot = EraIoT('" + wifi + "', '" + password + "', '" + token + "')\n";
  
  // TODO: Assemble Python into code variable.
  var code = "await era_iot.connect()\n";
  return code;
};

Blockly.Blocks["era_mqtt_publish"] = {
  init: function () {
    this.jsonInit({
      colour: "#ff8d12",
      nextStatement: null,
      tooltip: "Gửi thông tin lên server",
      message0: "gửi %1 %2 lên %3 %4",
      previousStatement: null,
      args0: [
        {
          type: "input_dummy",
        },
        {
          type: "input_value",
          name: "MESSAGE",
        },
        {
          type: "field_dropdown",
          name: "TOPIC",
          options: virtualPins,
        },
        {
          type: "input_dummy",
        }
      ],
      helpUrl: "",
    });
  },
};

Blockly.Python['era_mqtt_publish'] = function(block) {
  Blockly.Python.definitions_['import_era_iot'] = 'from era-iot import *';
  var message = Blockly.Python.valueToCode(block, 'MESSAGE', Blockly.Python.ORDER_ATOMIC);
  var topic = block.getFieldValue('TOPIC');
  // TODO: Assemble Python into code variable.
  Blockly.Python.definitions_['import_era_iot'] = 'from era_iot import *';
  var code = "await era_iot.virtual_write(" + topic + ", " + message + ")\n";
  return code;
};

Blockly.Blocks["era_mqtt_on_receive_message"] = {
  init: function () {
    this.jsonInit({
      colour: "#ff8d12",
      tooltip: "Khai báo lệnh xử lý khi có thông tin từ server cập nhật virtual pin",
      message0: "khi %1 nhận thông tin %2 %3",
      args0: [
        {
          type: "field_dropdown",
          name: "TOPIC",
          options: virtualPins,
        },
        { type: "input_dummy" },
        { type: "input_statement", name: "ACTION" },
      ],
      helpUrl: "",
    });
  },
};

Blockly.Python['era_mqtt_on_receive_message'] = function(block) {
  Blockly.Python.definitions_['import_era_iot'] = 'from era_iot import *';
  var topic = block.getFieldValue('TOPIC');
  var statements_action = Blockly.Python.statementToCode(block, 'ACTION');
  // TODO: Assemble Python into code variable.
  var globals = buildGlobalString(block);

  var cbFunctionName = Blockly.Python.provideFunction_(
    'on_era_virtual_pin_v' + topic,
    (globals != '')?
    ['async def ' + Blockly.Python.FUNCTION_NAME_PLACEHOLDER_ + '(topic, value):',
      globals,
      statements_action || Blockly.Python.PASS
    ]:
    ['async def ' + Blockly.Python.FUNCTION_NAME_PLACEHOLDER_ + '(topic, value):',
      statements_action || Blockly.Python.PASS
    ]);

    Blockly.Python.definitions_['import_era_iot'] = 'from era_iot import *';
    Blockly.Python.definitions_['task_era_virtual_pin_v' + topic] = "era_iot.on_virtual_read(" + topic + ", " + cbFunctionName + ")";

  return '';
};

Blockly.Blocks['era_mqtt_get_value'] = {
  init: function () {
    this.jsonInit(
      {
        "message0": "giá trị nhận được",
        "args0": [],
        "output": null,
        "colour": "#ff8d12",
        "tooltip": "Đọc giá trị nhận được từ server gửi đến",
        "helpUrl": ""
      }
    );
  }
};

Blockly.Python['era_mqtt_get_value'] = function (block) {
  // TODO: Assemble Python into code variable.
  Blockly.Python.definitions_['import_era_iot'] = 'from era_iot import *';

  var code = 'value';
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Blocks['era_mqtt_compare_value'] = {
  init: function () {
    this.jsonInit(
      {
        "message0": "giá trị nhận được là %1 %2",
        "args0": [
          {
            "type": "input_value",
            "name": "VALUE",
          },
          {
            type: "input_dummy"
          }
        ],
        "output": "Boolean",
        "colour": "#ff8d12",
        "tooltip": "Kiểm tra xem giá trị nhận được từ server có bằng giá trị được chọn hay không",
        "helpUrl": ""
      }
    );
  }
};

Blockly.Python['era_mqtt_compare_value'] = function (block) {
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_ATOMIC);
  // TODO: Assemble Python into code variable.
  Blockly.Python.definitions_['import_era_iot'] = 'from era_iot import *';
  var code = 'value == ' + value;
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};


Blockly.Blocks['era_mqtt_get_topic'] = {
  init: function () {
    this.jsonInit(
      {
        "message0": "topic nhận được",
        "args0": [],
        "output": null,
        "colour": "#ff8d12",
        "tooltip": "Đọc topic nhận được từ server gửi đến",
        "helpUrl": ""
      }
    );
  }
};

Blockly.Python['era_mqtt_get_topic'] = function (block) {
  // TODO: Assemble Python into code variable.
  Blockly.Python.definitions_['import_era_iot'] = 'from era_iot import *';

  var code = 'topic';
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};
