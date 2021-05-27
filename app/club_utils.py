import matplotlib.pyplot as plt

def showClubPositions(club):
    fig = plt.figure()
    fig.add_subplot(111)
    tables = club.league.leagueTables
    # Rank positions
    rankedTables = []
    for table in tables.values():
        rankedTable = []
        tableItems = list(table.items())
        tableItems.sort(key = lambda x: (x[1]['Pts'], x[1]['GD']), reverse = True)
        for i, tableItem in enumerate(tableItems, 1):
            tableItem[1]['Rank'] = i
            rankedTable.append(tableItem)
        rankedTables.append(rankedTable)
    ranks = []
    for rankedTable in rankedTables:
        for tableClub, tableData in rankedTable:
            if club == tableClub:
                ranks.append(tableData['Rank'])
    x = list(range(0, len(ranks)))
    y = ranks
    # plt.axis('off')
    plt.plot(x, y, 'b-')
    return fig