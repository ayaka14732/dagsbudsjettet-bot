from aiogram import Bot, Dispatcher, executor, types
import json
import locale

locale.setlocale(locale.LC_NUMERIC, 'nb_NO.UTF-8')

def load_config():
    with open('config.json') as f:
        o = json.load(f)
        api_token = o['api_token']
        user_id = int(o['user_id'])
    return api_token, user_id

API_TOKEN, USER_ID = load_config()

class GlobalState:
    def __init__(self) -> None:
        self.daily_budget = 0
        self.remaining_today = 0

    def set_daily_budget(self, budget: float) -> None:
        int_budget = int(budget * 10000)
        self.daily_budget = int_budget

    def get_daily_budget(self) -> float:
        return self.daily_budget / 10000

    def set_remaining_today(self, amount: float) -> None:
        int_amount = int(amount * 10000)
        self.remaining_today = int_amount

    def get_remaining_today(self) -> float:
        return self.remaining_today / 10000

    def use(self, budget: float) -> None:
        int_budget = int(budget * 10000)
        self.remaining_today -= int_budget

    def next_day(self) -> None:
        self.remaining_today += self.daily_budget

    def reset(self) -> None:
        self.daily_budget = 0
        self.remaining_today = 0

gs = GlobalState()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help', 'hjp'])
async def start(message: types.Message):
    if message.from_user.id != USER_ID:
        await message.answer('Feil. Denne boten er designet for kun én bruker.')
    else:
        await message.answer('''`/hjp`: Vis denne meldingen.
`/adb 10,00`: Angi dagsbudsjett.
`/fdb`: Få dagsbudsjett.
`/adg 3,52`: Angi dagens gjenstående beløp.
`/fdg`: Få dagens gjenstående beløp.
`/brk 3,95`: Bruk et bestemt beløp.
`/tnd`: Gå til neste dag.
`/nul`: Tilbakestille.''', parse_mode='Markdown')

@dp.message_handler(commands=['adb'])
async def adb(message: types.Message):
    if message.from_user.id != USER_ID:
        await message.answer('Feil. Denne boten er designet for kun én bruker.')
    else:
        text = message.get_args()
        text = text.split(' ', 1)[0]  # use the first argument only
        try:
            assert '.' not in text, 'Should use , for decimal separator instead'
            daily_budget = locale.atof(text)
            gs.set_daily_budget(daily_budget)
            str_daily_budget = locale.format_string('%.4f', gs.get_daily_budget())
            await message.answer(f'Dagsbudsjettet er satt til {str_daily_budget}.')
        except Exception:
            await message.answer('Feil. Bruk: `/adb 10,00`', parse_mode='Markdown')

@dp.message_handler(commands=['fdb'])
async def fdb(message: types.Message):
    if message.from_user.id != USER_ID:
        await message.answer('Feil. Denne boten er designet for kun én bruker.')
    else:
        try:
            str_daily_budget = locale.format_string('%.4f', gs.get_daily_budget())
            await message.answer(f'Dagsbudsjettet er {str_daily_budget}.')
        except Exception as e:
            await message.answer(str(e))

@dp.message_handler(commands=['adg'])
async def adg(message: types.Message):
    if message.from_user.id != USER_ID:
        await message.answer('Feil. Denne boten er designet for kun én bruker.')
    else:
        text = message.get_args()
        text = text.split(' ', 1)[0]  # use the first argument only
        try:
            assert '.' not in text, 'Should use , for decimal separator instead'
            remaining_today = locale.atof(text)
            gs.set_remaining_today(remaining_today)
            str_remaining_today = locale.format_string('%.4f', gs.get_remaining_today())
            await message.answer(f'Dagens gjenstående beløp er satt til {str_remaining_today}.')
        except Exception:
            await message.answer('Feil. Bruk: `/adg 3,52`', parse_mode='Markdown')

@dp.message_handler(commands=['fdg'])
async def fdg(message: types.Message):
    if message.from_user.id != USER_ID:
        await message.answer('Feil. Denne boten er designet for kun én bruker.')
    else:
        str_remaining_today = locale.format_string('%.4f', gs.get_remaining_today())
        await message.answer(f'Dagens gjenstående beløp er {str_remaining_today}.')

@dp.message_handler(commands=['brk'])
async def brk(message: types.Message):
    if message.from_user.id != USER_ID:
        await message.answer('Feil. Denne boten er designet for kun én bruker.')
    else:
        text = message.get_args()
        try:
            assert '.' not in text, 'Should use , for decimal separator instead'
            budget = locale.atof(text)
            gs.use(budget)
            str_budget = locale.format_string('%.4f', budget)
            str_remaining_today = locale.format_string('%.4f', gs.get_remaining_today())
            await message.answer(f'Du brukte {str_budget}. Dagens gjenstående beløp er {str_remaining_today}.')
        except Exception:
            await message.answer('Feil. Bruk: `/brk 3,95`', parse_mode='Markdown')

@dp.message_handler(commands=['tnd'])
async def tnd(message: types.Message):
    if message.from_user.id != USER_ID:
        await message.answer('Feil. Denne boten er designet for kun én bruker.')
    else:
        gs.next_day()
        str_remaining_today = locale.format_string('%.4f', gs.get_remaining_today())
        await message.answer(f'Ha en fin dag! Dagens budsjett er {str_remaining_today}.')

@dp.message_handler(commands=['nul'])
async def nul(message: types.Message):
    if message.from_user.id != USER_ID:
        await message.answer('Feil. Denne boten er designet for kun én bruker.')
    else:
        gs.reset()
        await message.answer(f'Tilbakestillingen var vellykket.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
