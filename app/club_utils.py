import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def showClubPositions(club):
    fig = plt.figure()
    fig.add_subplot(111)
    league = club.league
    tables = league.leagueTables
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
    for rankedTable in rankedTables[1:]:
        for tableClub, tableData in rankedTable:
            if club == tableClub:
                ranks.append(tableData['Rank'])
    x = list(range(0, len(ranks)))
    y = ranks
    for i in range(len(league.clubs) + 1):
        plt.gca().axhline(i, color = '#bbbbbb', linestyle = '--', linewidth = 0.75)
    for i in range((len(rankedTables))):
        if i % 10 == 0:
            plt.gca().axvline(i, color = '#bbbbbb', linestyle = '--', linewidth = 0.75)
    plt.plot(x, y, '-bo')
    plt.xlabel('Gameweek', fontsize = 12, fontweight = 'bold', labelpad = 8)
    plt.ylabel('League position', fontsize = 12, fontweight = 'bold', labelpad = 8)
    plt.ylim([0, len(league.clubs) + 1])
    plt.gca().invert_yaxis()
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    return fig