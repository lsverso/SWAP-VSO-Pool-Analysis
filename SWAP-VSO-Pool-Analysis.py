import pandas as pd
pd.set_option('display.max_rows', 10000)
import requests
import matplotlib.pyplot as plt

# load parameters for the covalenthq API url
API_KEY = 'ckey_e1328ce2b7104ccaa03d0955258'
chain_id = 43114
contract_address = '0x454d379Ba89EB7BdA6AAA0420B056bD03fcF012B'
page_size = 200_000
payload = {
                "key": API_KEY,
                "page-size": page_size,
                "block-signed-at-asc": True
            }


# load covalenthq API url with parameters
covalent_url = 'https://api.covalenthq.com/v1/' + str(chain_id) + "/address/" + contract_address + '/transactions_v2/?quote-currency=usd'
url = requests.get(url=covalent_url, params=payload)


# create empty list of transactions (will be populated with dictionaries later)
transaction_list = []


# load raw data from API and crete loop for all items (individual transactions)
items = url.json()['data']['items']
for item in items:
    log_events = item['log_events']

    # if the transaction is not a VSO transaction, skip to next log_event
    for log_event in log_events:
        if log_event['sender_contract_ticker_symbol'] != 'VSO':
            continue

        # create one dictionary per details/parameters of each transaction
        tx_params = {}

        block_height = log_event['block_height']
        tx_params['block_height'] = block_height

        tx_hash = log_event['tx_hash']
        tx_params['tx_hash'] = tx_hash
        # print(block_height, tx_hash)

        decoded = log_event['decoded']
        params = decoded['params']

        # some params objects are TypeNone, so skip those
        if params is None:
            continue

        # create for loop for each parameter (from (address), to (address), amount (value of VSO transaction))
        for param_dict in params:
            name = param_dict['name']

            if name == 'from':
                tx_params['from'] = param_dict['value']
                continue
            elif name == 'to':
                tx_params['to'] = param_dict['value']
                continue
            elif name == 'value':
                tx_params['amount'] = param_dict['value']

            # for each created dictionary of transaction parameters, add it to the empty list created in the beginning
            transaction_list.append(tx_params)


# create dataframe from transaction_list
df = pd.DataFrame(transaction_list)

# reformat 'amount' column into floats
df['amount'] = [float("{:.2f}".format(float(item) / 10 ** 18)) for item in df['amount']]

# drop row with initial deposit of 150,000 VSO into iceberg smart contract
df = df.drop(df.index[4]).reset_index(drop=True)

# group amount of VSO by receiving address ('to' column) and order by descending order
amount_grouped = df['amount'].groupby(df['to']).sum()
amount_per_address = amount_grouped.sort_values(ascending=False)
print(amount_per_address[1:])
print(len(df['to'].unique()))

# plot amount of rewarded VSO by address
plt.bar(df['to'].unique()[1:], amount_per_address[1:])
plt.show()

print(hi)