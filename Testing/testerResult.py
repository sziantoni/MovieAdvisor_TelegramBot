
def manageResults(ret, tester1, keywords):
    count = 0
    variable = tester1.split(' ')
    score_lists = []
    for v in variable:
        if len(v) <= 1:
            variable.remove(v)
    print('-----------------------------------------------------------------------------------------------\n')
    limit_value = 1
    for result in ret["results"]["bindings"]:
        if str(result["movie_title"]["value"]) != 'The Cutter':
            print(str(result["movie_title"]["value"]) + ' -> ' + str(result['score']['value']))
            print("Top KW VALUE " + str(result["top_kw"]["value"]))
            print('LINK: ' + result["link"]["value"])
            print('SUBJECT: ' + result["list"]["value"])
            print('ABSTRACT: ' + result["abstract"]["value"])
            if count == 0 or int(result['score']['value']) >= limit_value:
                print('-VALIDO-\n')
                if count == 0:
                    top_value = int(result['score']['value'])
                    limit_value = int(top_value / 1.5)
                count += 1
            else:
                print('-NON VALIDO-\n')
    print('-----------------------------------------------------------------------------------------------\n')
    return score_lists
