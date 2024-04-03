# CAN USB Software

Данный репозиторий содержит пакет программ, предназначенных для общения по CAN-шине с устройствами, основанными на STM32.С "железной" стороны используются USB-CAN преобразователь и библиотеки CANLib2, разработанные в ОАИ НГУ.

## Установка

Для установки используются [git](https://github.com/) и менеджер пакетов [pip](https://pip.pypa.io/en/stable/).

Bash:
```bash
git clone https://github.com/CuSynth/can_usb_software.git
cd ./can_usb_software/ && python -m venv .venv && source .venv/Scripts/activate && python -m pip install -r requirements.txt
```

PowerShell (в том числе, терминал VsCode):
```powershell
git clone https://github.com/CuSynth/can_usb_software.git
cd ./can_usb_software/
python -m venv .venv
.venv/Scripts/activate
python -m pip install -r requirements.txt
```


## Использование
Запустить файл **`can_unit.py`** из VsCode или из консоли:

Bash:
```bash
source .venv/Scripts/activate
python can_unit.py
```
PowerShell (в том числе, терминал VsCode):
```powershell
.venv/Scripts/activate
python can_unit.py
```

