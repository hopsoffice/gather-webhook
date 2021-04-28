# Gather webhook

[gather.town][] 웹사이트 인터랙션을 통해 슬랙과 통합합니다.


[gather.town]: https://gather.town


## 필요한 프로그램

- Python 3.8
- AWS 계정: 당장은 배포를 손으로해야하므로
- 슬랙 웹훅


## 설치

팀을 위한 설정이 필요합니다. `resource.json.tmpl`을 `resource.json`으로
복사합니다.

```
$ cp resource.json.tmpl resource.json
```

팀원 이름과 채팅을 전달하고 싶은 채널의 [수신 웹후크][incoming-webhook]을 만들어서 `"slack_hook"`에 넣어주세요.

```
$ cat resource.json
{
    "teamMates": ["someone", "likes", "you"],
    "slack_hook": "...."
}
```

[incoming-webhook]: https://slack.com/intl/ko-kr/help/articles/115005265063-Slack%EC%9A%A9-%EC%88%98%EC%8B%A0-%EC%9B%B9%ED%9B%84%ED%81%AC

자파 배포의 필요한 설정과 라이브러리를 설치합니다. `install.sh`에서 `zappa_settings.json`을 생성하니 참고해주세요.

```
$ python -m venv .venv
$ ./scripts/install.sh
```

## 배포

위 설치 과정을 거쳐서 처음 배포를 진행한다면 아래의 커맨드로 실행하면됩니다. 


```
$ zappa deploy dev
```

처음 배포 이후엔 대부분의 경우 코드를 고치고 업데이트만 하면됩니다.

```
$ zappa update dev
```

## API

### `/return/<이름>/`

"이름"님이 자리로 돌아옴을 슬랙 채널에 알립니다. 리소스의 `.["message"]["return"]` 값을 바꾸어 커스텀 메시지로 바꿀 수 있습니다.

### `/start/<이름>/`

"이름"님이 근무를 시작함을 슬랙 채널에 알립니다. 리소스의 `.["message"]["start"]` 값을 바꾸어 커스텀 메시지로 바꿀 수 있습니다.

### `/end/<이름>/`

"이름"님이 근무를 종료함을 슬랙 채널에 알립니다. 리소스의 `.["message"]["end"]` 값을 바꾸어 커스텀 메시지로 바꿀 수 있습니다.


### `/eat/`

팀원들이 밥을 먹으러 갈때 사용할 수 있는 메뉴입니다. `.["teamMates"]` 값을 가지고 팀원들 이름을 만들기 떄문에 값 설정을 꼭 해야합니다.


### `/rest/`

팀원들이 쉬러 갈때 사용할 수 있는 메뉴입니다. `.["teamMates"]` 값을 가지고 팀원들 이름을 만들기 떄문에 값 설정을 꼭 해야합니다.


### `/do/`

팀원들이 아무말이나 적고 자리를 비울때 사용할 수 있는 메뉴입니다. `.["teamMates"]` 값을 가지고 팀원들 이름을 만들기 떄문에 값 설정을 꼭 해야합니다.


## 게더타운 준비

이제 모든 준비가 끝났다면, 게더타운에서 오브젝트를 만들때 자파로 배포한
어플리케이션의 주소를 이용하여 하고 싶은 액션에 따라 주소를 바꾸면됩니다.

예를 들어 `https://some-api-gateway.aws.amazone.com/dev/`가 자파로 배포된
어플리케이션의 주소라면, `https://some-api-gateway.aws.amazone.com/dev/start/Ed/`
라는 웹사이트 주소를 오브젝트에 적어주면 슬랙채널에 알림이 가게됩니다.

웹사이트 임베드에 대해서 모르신다면, [게더타운 페이지][help-gather]에서
"Embedded Websites" 항목을 참고해주세요.

[help-gather]: https://support.gather.town/help/objects
