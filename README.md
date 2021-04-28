# Gather webhook

[gather.town][] 웹사이트 인터랙션을 통해 슬랙과 통합합니다.


[gather.town]: https://gather.town


## 필요한 프로그램

- Python 3.8
- AWS 계정: 당장은 배포를 손으로해야하므로
- 슬랙 웹훅


## 설치

```
$ python -m venv .venv
$ ./scripts/install.sh
```

## 배포

처음 배포를 진행한다면 아래의 커맨드로 실행하면됩니다. 


```
$ zappa deploy dev
```

처음배포 이후이엔 대부분의 경우엔 코드를 고치고 업데이트만 하면됨

```
$ zappa update dev
```

## API

### `/`

