# RGB-BTW 🌈

Управление RGB светодиодными лентами через MQTT с помощью удобной CLI утилиты и прошивки для ESP8266.

![MQTT](https://img.shields.io/badge/MQTT-Enabled-brightgreen)
![ESP8266](https://img.shields.io/badge/ESP8266-Compatible-orange)
![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 О проекте

RGB-BTW (RGB By The Way) - это система для удаленного управления RGB светодиодными лентами через протокол MQTT. Проект состоит из двух основных компонентов:

- **CLI утилита** на Python для управления устройствами с компьютера
- **Прошивка** для ESP8266 с поддержкой WS2812/NeoPixel лент

## ✨ Особенности

- 🎨 Поддержка 20+ предустановленных цветов
- 🌈 Режим радуги с плавными переходами
- 💾 Сохранение состояния в EEPROM (после перезагрузки настройки сохраняются)
- 📱 Удобное CLI управление с подсветкой синтаксиса
- 🔧 Поддержка множества устройств
- 📊 Мониторинг текущего состояния ленты

## 🗂️ Структура проекта
```
.
├── cli/ # CLI утилита на Python
│ ├── main.py # Основной скрипт
│ ├── requirements.txt # Зависимости Python
│ └── db.db # База данных устройств
├── ino_scripts/ # Прошивка для ESP8266
│ └── main.ino # Основной скетч
├── .gitignore # Git ignore файл
└── LICENSE # Лицензия MIT
```

## 🚀 Быстрый старт

### Установка CLI утилиты

```bash
cd cli
pip install -r requirements.txt
python main.py init
```

### Добавление устройства
```bash
python main.py add my_lamp \
  --host mqtt.broker.com \
  --port 1883 \
  --user username \
  --passwd password \
  --topic rgb/lamp
```

### Управление устройством
```bash
# Включить/выключить
python main.py set my_lamp --toggle

# Установить цвет
python main.py set my_lamp --color blue

# Установить RGB значения
python main.py set my_lamp --rgbR 255 --rgbG 100 --rgbB 50

# Включить режим радуги
python main.py set my_lamp --rainbow

# Изменить яркость
python main.py set my_lamp --brightness 150

# Получить текущее состояние
python main.py get my_lamp
```

## 🔧 Настройка прошивки
Перед загрузкой прошивки на ESP8266 необходимо настроить параметры в файле `main.ino`:
```cpp
// Wi-Fi настройки
const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";

// MQTT настройки
const char* mqtt_server = "your.mqtt.broker";
const int mqtt_port = 1883;
const char* mqtt_user = "mqtt_username";
const char* mqtt_password = "mqtt_password";
const char* mqtt_topic = "rgb/lamp";

// Подключение ленты
#define led_strip 15        // Пин подключения
#define pixels_count 5      // Количество светодиодов
```

## 📖 Поддерживаемые цвета
Проект поддерживает 20+ предустановленных цветов:

- `red`, `green`, `blue`, `white`, `black`

- `yellow`, `cyan`, `magenta`, `orange`, `purple`

- `pink`, `brown`, `gray`, `lightgray`, `darkgray`

- `lime`, `maroon`, `navy`, `olive`, `teal`
## 🔌 Подключение оборудования
```
ESP8266 → WS2812/NeoPixel лента
   GPIO15 → Data In
   5V/VIN → 5V
   GND → GND
```
_Рекомендуется использовать внешний источник питания для ленты при большом количестве светодиодов._
## 📝 Лицензия
Проект распространяется под лицензией MIT. Подробнее см. в файле [LICENSE](license).
## 🤝 Вклад в проект
Приветствуются pull requests и issue reports! Для крупных изменений пожалуйста, откройте issue сначала для обсуждения предлагаемых изменений.

---

**RGB-BTW** - сделайте ваше освещение умнее и красочнее! ✨