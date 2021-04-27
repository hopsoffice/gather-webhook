## Installation

### Requirements

- Python 3.8
- zappa
- [galbi][]
- aws 계정: 당장은 배포를 손으로해야하므로


### Scripts

```
$ python -m venv .venv
$ pip install zappa galbi
$ ./scripts/install.sh
```

## Deploy

대부분의 경우엔 코드를 고치고 업데이트만 하면됨

```
$ zappa deploy dev
```


[galbi]: https://github.com/hopsoffice/galbi
