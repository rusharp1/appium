from carrot_like import CarrotLikeBot  # (1) 좋아요 봇
from carrot_read_like import CarrotProfileReader  # (2) 프로필 리더

def verify_likes():
    # (1) 좋아요 누르고 제목 목록 받아오기
    print("좋아요 봇 시작")
    like_bot = CarrotLikeBot()
    liked_results = like_bot.run()  # 결과 딕셔너리 받아오기
    liked_titles = liked_results['liked_titles']  # 좋아요 누른 제목들 리스트
    print(f"좋아요 누른 제목 {len(liked_titles)}개: {liked_titles}")
    
    # (2) 프로필 리더로 관심목록 받아오기
    print("\n프로필 리더 시작...")
    profile_reader = CarrotProfileReader()
    profile_titles = profile_reader.run()  # 프로필의 관심목록 제목들
    print(f"프로필 관심목록 {len(profile_titles)}개: {profile_titles}")
    
    # (1)의 모든 항목이 (2)에 포함되어 있는지 확인
    print("\n검증 시작...")
    
    missing_titles = []
    for liked_title in liked_titles:
        if liked_title not in profile_titles:
            missing_titles.append(liked_title)
    
    # 결과 판정
    if len(missing_titles) == 0:
        print("PASS: 좋아요 누른 모든 항목이 프로필 관심목록에 포함되어 있습니다!")
        return True
    else:
        print(f"FAIL: {len(missing_titles)}개 항목이 프로필에서 누락됨")
        print(f"누락된 항목들: {missing_titles}")
        return False

def main():
    """메인 실행 함수"""
    try:
        result = verify_likes()
        
        if result:
            print("\n검증 성공!")
        else:
            print("\n검증 실패!")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()