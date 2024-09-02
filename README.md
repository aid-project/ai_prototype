# AId-AIServer
# 주의사항
private key들이 담겨있는 setting.py가 여기 Repo에 없음.
## requirements.txt(동일한 환경) 사용하기:
### virtualenv 설치
pip install virtualenv
### 가상환경 구성
virtualenv venv --python=python3.9

## module 관련
### requirements.txt 생성
가상 환경에서 pip freeze > requirements.txt 명령을 실행하여 현재 설치된 패키지 목록을 requirements.txt 파일로 내보냅니다.
requirements.txt 파일을 GitHub에 추가 및 커밋합니다.
### requirements.txt로 모듈 설치
다른 개발자가 프로젝트를 클론한 후, 해당 디렉토리에서 가상 환경을 만들고 pip install -r requirements.txt 명령을 실행하여 종속성을 설치합니다.
