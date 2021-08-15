
# 상품글이면 가운데정렬


def trace(func):                             # 호출할 함수를 매개변수로 받음
    def wrapper():
        print(func.__name__, '함수 시작')    # __name__으로 함수 이름 출력
        func()                               # 매개변수로 받은 함수를 호출
        print(func.__name__, '함수 끝')
    return wrapper                           # wrapper 함수 반환


class IsMultiple:
    def __init__(self, x):  # 데코레이터가 사용할 매개변수를 초깃값으로 받음
        self.x = x  # 매개변수를 속성 x에 저장

    def __call__(self, func):  # 호출할 함수를 매개변수로 받음
        def wrapper(a, b):  # 호출할 함수의 매개변수와 똑같이 지정(가변 인수로 작성해도 됨)
            r = func(a, b)  # func를 호출하고 반환값을 변수에 저장
            if r % self.x == 0:  # func의 반환값이 self.x의 배수인지 확인
                print('{0}의 반환값은 {1}의 배수입니다.'.format(func.__name__, self.x))
            else:
                print('{0}의 반환값은 {1}의 배수가 아닙니다.'.format(func.__name__, self.x))
            return r  # func의 반환값을 반환

        return wrapper  # wrapper 함수 반환


@IsMultiple(3)  # 데코레이터(인수)
def add(a, b):
    return a + b


print(add(10, 20))
print(add(2, 5))


def trace(func):  # 호출할 함수를 매개변수로 받음
    def wrapper(*args, **kwargs):  # 가변 인수 함수로 만듦
        r = func(*args, **kwargs)  # func에 args, kwargs를 언패킹하여 넣어줌
        print('{0}(args={1}, kwargs={2}) -> {3}'.format(func.__name__, args, kwargs, r))
        # 매개변수와 반환값 출력
        return r  # func의 반환값을 반환

    return wrapper  # wrapper 함수 반환


@trace  # @데코레이터
def get_max(*args):  # 위치 인수를 사용하는 가변 인수 함수
    return max(args)


@trace  # @데코레이터
def get_min(**kwargs):  # 키워드 인수를 사용하는 가변 인수 함수
    return min(kwargs.values())


print(get_max(10, 20))
print(get_min(x=10, y=20, z=30))

def is_multiple(x):  # 데코레이터가 사용할 매개변수를 지정
    def real_decorator(func):  # 호출할 함수를 매개변수로 받음
        def wrapper(a, b):  # 호출할 함수의 매개변수와 똑같이 지정
            r = func(a, b)  # func를 호출하고 반환값을 변수에 저장
            if r % x == 0:  # func의 반환값이 x의 배수인지 확인
                print('{0}의 반환값은 {1}의 배수입니다.'.format(func.__name__, x))
            else:
                print('{0}의 반환값은 {1}의 배수가 아닙니다.'.format(func.__name__, x))
            return r  # func의 반환값을 반환

        return wrapper  # wrapper 함수 반환

    return real_decorator  # real_decorator 함수 반환


@is_multiple(3)  # @데코레이터(인수)
def add(a, b):
    return a + b


print(add(10, 20))
print(add(2, 5))


def trace(func):
    def wrapper(self, a, b):  # 호출할 함수가 인스턴스 메서드이므로 첫 번째 매개변수는 self로 지정
        r = func(self, a, b)  # self와 매개변수를 그대로 넣어줌
        print('{0}(a={1}, b={2}) -> {3}'.format(func.__name__, a, b, r))  # 매개변수와 반환값 출력
        return r  # func의 반환값을 반환

    return wrapper


class Calc:
    @trace
    def add(self, a, b):  # add는 인스턴스 메서드
        return a + b


c = Calc()
print(c.add(10, 20))