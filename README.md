## Usage

```
python expert_system.py <file>
```

## Usage of tests

***Run at the root:***

Test all 136 files(bad and good):
```
pytest tests/test_examples.py
```

Test 52 files(only good):
```
pytest tests/test_correction.py
```

## Bonuses

```
1. Color
2. If and only if (<=>)
3. Tester
```


### Используемая литература

https://medium.com/a-42-journey/expert-systems-how-to-implement-a-backward-chaining-resolver-in-python-bf7d8924f72f

https://studizba.com/lectures/10-informatika-i-programmirovanie/302-iskusstvennyy-intellekt/4026-62-pryamoy-i-obratnyy-vyvod.html

https://www.programiz.com/python-programming/methods/built-in/staticmethod#:~:text=What%20is%20a%20static%20method,the%20state%20of%20the%20object.

https://ru.wikipedia.org/wiki/Обратная_польская_запись

[Давайте разберемся с нижним подчеркиванием (_) в Python](https://zen.yandex.ru/media/nuancesprog/davaite-razberemsia-s-nijnim-podcherkivaniem--v-python-5dcef95724f3107fe31471d9)

#### Вопросы по заданию

##### В задании не сказано, что *input* файл должен заканчиваться на *'\n'*. 
Если необходимо, чтобы выводилась ошибка, 
если файл не заканчивается на пустую строку, 
то нужно раскомментировать строчки в файле ***parser.py***