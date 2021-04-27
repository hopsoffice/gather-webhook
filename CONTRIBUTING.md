# landing webhook contribution guide

개발하는데 도움이 되는 잡다한 지식들

## zappa

람다에 파이썬 앱을 쉽게 배포할 수 있게 도와준다. 이 어플리케이션은 zappa로
배포되기 때문에 가급적이면 랜딩 웹훅과 관련된 아주 간단한 작업만 포함해야한다.

패키지는 virtual environment에 깔린 모든 패키지를 같이 업로드하기 때문에
사용하지 않는 패키지는 삭제 후에 배포해야 한다.

### zappa_settings.json

zappa 배포에 필요한 설정 파일인데 `scripts/install.sh`로 만들 수 있다.


## 설정 관리

버전관리와 별도로 관리해야하는 설정은 galbi로 저장해서 쓰고,
`scripts/install.sh`와 `scripts/build.py`를 고쳐야한다.

`scripts/install.sh`에 `galbi get`하는 부분을 고쳐야하고, `scripts/build.py`에 `template`와 `m` 변수를 고쳐야한다.


## 인증

구글 스프레드 시트에 기록하기 때문에 구글 스프레드 시트를 사용하기 위한
oauth 토큰을 s3에 저장한다. `/oauth/` API 에서 저장되며,  혹시나 에러 알림이
난다면 배포된 url의 `/auth/`를 접속하여 oauth 인증을 해주면된다.
