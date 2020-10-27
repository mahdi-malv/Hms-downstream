# Hms downstream sender

A python script that gathers these things:

- Retrieve `access_token` from server
- Cache token considering one hour expire time
- Send message

## Usage

Supports:
- [x] Data message
- [ ] Notifications


Prerequisites: **Python3**

### dependencies

1. `pip`
```
pip install -r requirements.txt
```
2. config file

Add the following fields in `hms_config.txt` config file beside the script:

* `client_id`: From Huawei console (`appId`)
* `client_secret`: From Huawei console (`appSecret`)

### Run the script:

```
python3 hms_send.py [OPTIONS]
# also with bash ./hms_send.py
```

**Options**:

|Option|Desc|
|:--:|:--|
|`-t`/`--tokens` [TOKEN1 ...]| List of hms tokens to send the message to|
|`-d`/`--data`|Data to send as data message.<br>Data messages can be either Json or String. To pass json you must Wrap the wole json in double quotes(`"`) and use single quoutes to for json keys and values.<br>For example `-d "{'key':'value'}"`. Otherwise HMS might not be able to parse it on the clientside.|
|`-v`/`--verbose`|See debug logs of script|

#### Example

`hms_config.txt`:
```
[DEFAULT]
client_id = 1234565
client_secret = c73sdsdsgdfgdfh4te4jg43ju95jmgor35bd9260
```
> Notice the `[DEFAULT]`

`Command`:
```
python3 hms_send.py \
-t aToken anotherToken \
-d "{'key1':'value2', 'nestedKey1':{'nkey1':'nvalue1'}}" \
-v
```