import turtle as bot

lati = 10
lunghezza = 100
disegno = 1


n_figure = 3

def figura_utente(lati, lunghezza):
    bot.pendown()
    angolo = 360 / lati
    for x in range(lati):
        bot.pendown()
        bot.forward(lunghezza)
        bot.penup()
        bot.right(angolo)


def figura_utente_composta(lati, lunghezza):
    bot.pendown()
    angolo = 360 / lati
    angolo_interno = 360 / n_figure
    for y in range(n_figure):
        for x in range(lati):
            bot.pendown()
            bot.forward(lunghezza)
            bot.penup()
            bot.right(angolo)
        bot.right(angolo_interno)

if disegno == 1:
    figura_utente(lati, lunghezza)
    
if disegno == 2:
    figura_utente_composta(lati, lunghezza)

bot.penup()
bot.done()
