
def manageResults(ret, tester1, keywords, f):
    previous_value = 0
    count = 0
    variable = tester1.split(' ')
    for v in variable:
        if len(v) <= 1:
            variable.remove(v)
    print('-----------------------------------------------------------------------------------------------\n')
    f.write('KEYWORDS: \n')
    for k in keywords:
        f.write(str(k[0]) + ' : ' + str(k[1])  + '\n')
    for result in ret["results"]["bindings"]:
        print(str(result["movie_title"]["value"]) + ' -> ' + str(result['score']['value']))
        f.write("\n")
        f.write('\n' + str(result["movie_title"]["value"]) + ' -> ' + str(result['score']['value']) + '\n')
        f.write("\n")
        scoreList = ''
        for v in variable:
            v = v.replace('?' ,'')
            if result[v]['value'] != '0':
                scoreList = scoreList + ' | ' + v + ' : ' + str(result[v]['value'])
        f.write("\n")
        print(scoreList)
        f.write(scoreList  + '\n')
        f.write("\n")
        print('LINK: ' + result["link"]["value"])
        print('ABSTRACT: ' + result["abstract"]["value"])
        f.write('LINK: ' + result["link"]["value"] + '\n')
        f.write("\n")
        f.write('ABSTRACT: ' + result["abstract"]["value"] + '\n')
        f.write("\n")
        if int(result['score']['value']) > previous_value - 30 or (
                count == 0 and int(result['score']['value']) > 10) or int(result['score']['value']) > 90:
            print('-VALIDO-\n')
            f.write('-VALIDO-\n')
            f.write("\n")
            previous_value = int(result['score']['value'])
            count += 1
        else:
            print('-NON VALIDO-\n')
            f.write('-NON VALIDO-\n')
            f.write("\n")
    print('-----------------------------------------------------------------------------------------------\n')
