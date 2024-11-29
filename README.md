# logapi
[2024-11-15] 작업자 : 양재원
희수가 만들어 놓은거 일부 모듈화 했음.
작동은 하지만 테스트 아직 못해봄.

[2024-11-18] 작업자 : 김희수
error_log DB 데이터 추가.
일자별 로그 발생 빈도 시각화 코드 수정.
로그 레벨 분포 분석 및 시각화 코드 추가.

[2024-11-19] 작업자 : 김희수
dashborad.py 추가 -> localhost:8050
에러 로그가 하루 동안 쌓인 데이터라 가정하고 원하는 시간대와 에러 레벨에 따라 필터링 및 그래프로 표시

[2024-11-20] 작업자 : 김희수
dashborad.py 제거 -> flask로 실행 되도록 변경  
DB에 저장된 모든 로그를 대시보드로 확인 - viewlogs/show_logs  

[2024-11-21] 작업자 : 김희수  
error_distribution_chart 수정 -> html 파일 없이 대시보드화

[2024-11-25] 작업자 : 김희수
##### 실시간으로 로그 파일 가져옴 - access, error 분류 후 txt 파일에 저장 - DB에 저장 - txt파일 초기화 - (반복) / 테스트 못해봄
read_logs() : 실시간 로그 파일 읽기  
initialize_log_file() : txt 파일 초기화  
save_to_txt() : 로그 데이터 텍스트 파일에 저장  
def classify_and_save_logs() : 에러 로그와 접근 로그를 분류 후 저장  
def process_logs() : 실체 처리 / log_file_path 지정 필요  
