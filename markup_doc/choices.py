front_labels = [
    ('<abstract>', '<abstract>'),
    ('<abstract-title>', '<abstract-title>'),
    ('<aff>', '<aff>'),
    ('<article-id>', '<article-id>'),
    ('<article-title>', '<article-title>'),
    ('<author-notes>', '<author-notes>'), 
    ('<contrib>', '<contrib>'),
    ('<date-accepted>', '<date-accepted>'),
    ('<date-received>', '<date-received>'),
    ('<fig>', '<fig>'),
    ('<fig-attrib>', '<fig-attrib>'),
    ('<history>', '<history>'),
    ('<kwd-title>', '<kwd-title>'),
    ('<kwd-group>', '<kwd-group>'),
    ('<list>', '<list>'),
    ('<p>', '<p>'),
    ('<sec>', '<sec>'),
    ('<sub-sec>', '<sub-sec>'),
    ('<subject>', '<subject>'),
    ('<table>', '<table>'),
    ('<table-foot>', '<table-foot>'),
    ('<title>', '<title>'),
    ('<trans-abstract>', '<trans-abstract>'),
    ('<trans-title>', '<trans-title>'),
    ('<translate-front>', '<translate-front>'),
    ('<translate-body>', '<translate-body>'),
    ('<disp-formula>', '<disp-formula>'),
    ('<inline-formula>', '<inline-formula>'),
    ('<formula>', '<formula>'),
    
]

order_labels = {
    '<article-id>':{
        'pos' : 1,
        'next' : '<subject>'
    },
    '<subject>':{
        'pos' : 2,
        'next' : '<article-title>'
    },
    '<article-title>':{
        'pos' : 3,
        'next' : '<trans-title>',
        'lan' : True
    },
    '<trans-title>':{
        'size' : 14,
        'bold' : True,
        'lan' : True,
        'next' : '<contrib>'
    },
    '<contrib>':{
        'reset' : True,
        'size' : 12,
        'next' : '<aff>'
    },
    '<aff>':{
        'reset' : True,
        'size' : 12,
    },
    '<abstract>':{
        'size' : 12,
        'bold' : True,
        'lan' : True,
        'next' : '<p>'
    },
    '<p>':{
        'size' : 12,
        'next' : '<p>',
        'repeat' : True
    },
    '<trans-abstract>':{
        'size' : 12,
        'bold' : True,
        'lan' : True,
        'next' : '<p>'
    },
    '<kwd-group>':{
        'size' : 12,
        'regex' : r'(?i)(palabra.*clave.*:|keyword.*:)',
    },
    '<history>':{
        'size' : 12,
        'regex' : r'\d{2}/\d{2}/\d{4}',
    },
    '<corresp>':{
        'size' : 12,
        'regex' : r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    },
    '<sec>':{
        'size' : 16,
        'bold' : True,
        'next' : None
    },
    '<sub-sec>':{
        'size' : 12,
        'italic' : True,
        'next' : None
    },
    '<sub-sec-2>':{
        'size' : 14,
        'bold' : True,
        'next' : None 
    },
}

order_labels_body = {
    '<sec>':{
        'size' : 16,
        'bold' : True,
    },
    '<sub-sec>':{
        'size' : 12,
        'italic' : True,
    },
    '<p>':{
        'size' : 12,
    },
}