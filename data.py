# import constants as C

hearts = {'❤', '💛', '💚', '💙', '💜', '🖤', '❣', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '♥', } # '💔',

sm_resp = {
    'wlc': ('всегда пожалуйста', 'всегда рад', 'обращайся',),
    'hi': ('привет', 'салют', 'здравствуй',),
    'hi_smiles': ('🤗', '👋', ), # 'hugging', 'wave'
    'fun_smiles': ('🙂', '😃', '😁', '😀', '😄', '😏', '😉', '🙃'),
    'bye': ('пока', 'покеда', 'до свидания', 'всего хорошего',),
    'love': ('нравишься', 'люблю', 'heart', 'love', 'чмоки', 'kiss', ),
    'check_like': ('классный', 'получше', 'получше', 'милый', 'забавный', 'милашка', 'умница', 'хороший', ),
    'yes': ('да', 'да, конечно', 'разумеется', 'определённо', ),
    'no': ('нет', 'конечно нет', 'разумеется нет', 'определённо нет', ),
    'bot_dog': ('мальчик', 'фас', 'песик', 'пес', 'апорт', 'сидеть', 'лежать', 'голос', 'угол', 'лапу', 'собака',
                'блохастый', 'блохастик', 'сучка',),
    'apoliticality': (
        'Я - Сородич. То, как другие называют и определяют себя, касается меня только в тех случаях, '
            'когда связано с местными обычаями.',
    ),
    'not_funny_sm': (
        ':confused:', ':neutral_face:', ':unamused:',
    ),
    'not_funny_t': (
        ':confused:', ':neutral_face:', ':unamused:',
        'обхохочешься', '*очень смешно*', 'скажи, когда надо смеяться', 'ну, не уметь в юмор не самое страшное',
    ),
}
sm_resp['hi_plus'] = sm_resp['hi'] + sm_resp['hi_smiles']
sm_resp['not_funny'] = sm_resp['not_funny_sm'] + sm_resp['not_funny_t']
sm_resp['check_love'] = set(sm_resp['love']).union(hearts).union({'😘', '😗', '😽', '😚', '😙', '💋',})
sm_resp['ans_smiles'] = set(sm_resp['hi_smiles']).union(sm_resp['not_funny_sm']).union(sm_resp['fun_smiles'])

tremer_joke = 'Если вы переспросите, то я буду всё отрицать, но Тремер – мой любимый клан.'

forbiddenLinks = {
    'wod.su',
    'sabbat.su',
    'вот.су',
    'вод.су',
    'саббат.су',
}

# Dynamic data (not saved memory)

day_events = set()
