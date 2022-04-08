import json
import os

import dearpygui.dearpygui as dpg
import eth_utils
from cryptography.fernet import Fernet

from env_vars import (
    gas_price,
    lootbox_contract_arbitrum,
    lootbox_contract_rinkeby,
    web3_local_rinkeby,
    web3_arbitrum_rinkeby,
    dai_contract_rinkeby,
    dev
)

dpg.create_context()

web3_arbitrum_rinkeby.eth.account.enable_unaudited_hdwallet_features()

accounts_list = []

with dpg.font_registry():
    default_font = dpg.add_font("../fonts/m5x7.ttf", 25)
    created_account_font = dpg.add_font("../fonts/m5x7.ttf", 18)


# ---------
# Callbacks
# ---------

def create_account(new_eth_account, mnemonic, wallet_key):
    if not os.path.exists("accounts.json"):
        no_plaintext = Fernet(wallet_key)
        mnemonic_phrase = no_plaintext.encrypt(bytes(mnemonic, encoding='utf8'))
        pub_address = no_plaintext.encrypt(bytes(new_eth_account.address, encoding='utf8'))
        private_key = no_plaintext.encrypt(bytes(new_eth_account.key.hex(), encoding='utf8'))

        decrypt_pub_address = no_plaintext.decrypt(pub_address).decode("utf-8")
        decrypt_mnemonic_phrase = no_plaintext.decrypt(mnemonic_phrase).decode("utf-8")
        decrypt_private_key = no_plaintext.decrypt(private_key).decode("utf-8")

        save_account_info(decrypt_pub_address, mnemonic_phrase, private_key)
        show_created_account_info("Account info", decrypt_pub_address, decrypt_private_key, wallet_key,
                                  decrypt_mnemonic_phrase)
    else:
        print("Account already exists!!!")


def save_account_info(decrypt_pub_address, mnemonic_phrase, private_key):
    account = {'number': int(0), 'public_address': decrypt_pub_address, 'private_key': str(private_key.decode("utf-8")),
               'mnemonic_phrase': str(mnemonic_phrase.decode("utf-8"))}
    accounts_list.append(account)

    json.dump(accounts_list, open('accounts.json', 'w'))


def create_eth_account_callback():
    new_eth_account, mnemonic = web3_arbitrum_rinkeby.eth.account.create_with_mnemonic()
    wallet_key = Fernet.generate_key().decode("utf-8")
    create_account(new_eth_account, mnemonic, wallet_key)


def import_address_callback(mnemonic_phrase):
    try:
        new_eth_account = web3_arbitrum_rinkeby.eth.account.from_mnemonic(str(mnemonic_phrase))
        wallet_key = Fernet.generate_key().decode("utf-8")
        create_account(new_eth_account, mnemonic_phrase, wallet_key)
    except eth_utils.exceptions.ValidationError as e:
        print(e)


def import_multiple_accounts_callback(mnemonic_phrase, number_of_accounts):
    try:
        multiple_accounts_list = []
        iterator = 0
        wallet_key = Fernet.generate_key().decode("utf-8")
        no_plaintext = Fernet(wallet_key)

        if os.path.exists("accounts.json"):
            with open('accounts.json', 'r') as accounts:
                account_data = json.load(accounts)

        for account in range(int(number_of_accounts)):
            try:
                if account_data[account]:
                    print("Account exists!!!!!")
            except IndexError as e:
                print("Account does not exist")
                multiple_accounts_list.append(account)
                print(multiple_accounts_list)

        for number in multiple_accounts_list:
            new_eth_account = web3_arbitrum_rinkeby.eth.account.from_mnemonic(mnemonic_phrase,
                                                                              account_path=f"m/44'/60'/0'/0/{number}")

            pub_address = no_plaintext.encrypt(bytes(new_eth_account.address, encoding='utf8'))
            private_key = no_plaintext.encrypt(bytes(new_eth_account.key.hex(), encoding='utf8'))

            account = {'number': int(number), 'public_address': str(pub_address.decode("utf-8")),
                       'private_key': str(private_key.decode("utf-8"))}
            show_created_account_info("Account info", pub_address, wallet_key, private_key, "")
            accounts_list.append(account)
        json.dump(accounts_list, open('accounts.json', 'w'))
        multiple_accounts_list.clear()

    except eth_utils.exceptions.ValidationError as e:
        print(e)


def transfer_nft_thelootbox_callback(nft_contract_address, token_id):
    send_nft = lootbox_contract_arbitrum.functions.lootBox(nft_contract_address, token_id, dev).buildTransaction(
        {'gas': gas_price, 'nonce': web3_arbitrum_rinkeby.eth.getTransactionCount(dev, 'pending')})
    transaction = web3_arbitrum_rinkeby.eth.send_transaction(send_nft)


def create_bundle_callback(callback):
    try:
        # Approve transaction
        approve = dai_contract_rinkeby.functions.approve('0xE742e87184f840a559d26356362979AA6de56E3E',
                                                         10000000000000000000).buildTransaction(
            {'chainId': 4, 'gas': web3_local_rinkeby.toWei('0.02', 'gwei'),
             'nonce': web3_local_rinkeby.eth.get_transaction_count(dev, 'pending'), 'from': dev})
        send_approve_transaction = web3_local_rinkeby.eth.send_transaction(approve)

        # Create bundle
        create_bundle = lootbox_contract_rinkeby.functions.createBundle(10000000000000000000).buildTransaction(
            {'chainId': 4, 'gas': web3_local_rinkeby.toWei('0.02', 'gwei'),
             'nonce': web3_local_rinkeby.eth.get_transaction_count(dev, 'pending'), 'from': dev})
        send_bundle_transaction = web3_local_rinkeby.eth.send_transaction(create_bundle)
    except Exception as e:
        print(e)


def show_specific_account(account_id, wallet_key):
    no_plaintext = Fernet(wallet_key)
    with open('accounts.json', 'r') as accounts_from_file:
        account_data_json = json.load(accounts_from_file)
        pub_address = account_data_json[int(account_id)]['public_address']
        decrypt_private_address = no_plaintext.decrypt(
            bytes(account_data_json[int(account_id)]['private_key'], encoding='utf8'))
        show_created_account_info("Account info", pub_address, decrypt_private_address, wallet_key, "")


def send_ether_callback(to_account, amount_of_ether):
    tx = {
        'nonce': web3_arbitrum_rinkeby.eth.get_transaction_count(dev, 'pending'),
        'to': to_account,
        'value': web3_arbitrum_rinkeby.toWei(amount_of_ether, 'ether'),
        'gas': web3_arbitrum_rinkeby.toWei('0.02', 'gwei'),
        'gasPrice': gas_price,
        'from': dev
    }

    send_transaction = web3_arbitrum_rinkeby.eth.send_transaction(tx)
    work_pls = web3_arbitrum_rinkeby.eth.wait_for_transaction_receipt(send_transaction.hex())


# ----------------
# Selection events
# ----------------

def on_selection(sender, unused, user_data):
    print(user_data)
    if user_data[1]:
        callback = user_data[1]
        if user_data[2] == "Create account":
            create_eth_account_callback()
        if user_data[2] == "Create bundle":
            create_bundle_callback(callback)
        if user_data[2] == "Account info":
            key_to_bytes = bytes(dpg.get_value(user_data[3]), encoding='utf8')
            show_specific_account(key_to_bytes, user_data[4])
        if user_data[2] == "Transfer nft TheLootBox":
            nft_contract_address = dpg.get_value(user_data[3])
            token_id = dpg.get_value(user_data[4])
            transfer_nft_thelootbox_callback(nft_contract_address, token_id)
        if user_data[2] == "Send Ether":
            to_account = user_data[3]
            amount = user_data[4]
            send_ether_callback(to_account, amount)
        if user_data[2] == "Import Account":
            import_address_callback(dpg.get_value(user_data[3]))
        if user_data[2] == "Import Multiple Accounts":
            import_multiple_accounts_callback(dpg.get_value(user_data[3]), dpg.get_value(user_data[4]))
    else:
        dpg.delete_item(user_data[0])


# ----------------
# Prompts
# ----------------

def show_import_multiple_accounts_notification(title, message):
    with dpg.mutex():
        with dpg.window(label=title, width=700, height=400, modal=True) as modal_id:
            alert_message_group = dpg.add_group(horizontal=True)
            dpg.add_text(message)
            mnemonic_group = dpg.add_group(horizontal=True)
            dpg.add_text("Input mnemonic", pos=(10, 200), parent=mnemonic_group)
            mnemonic_phrase = dpg.add_input_text(parent=mnemonic_group)
            dpg.add_text("Input number of accounts", pos=(10, 250), parent=mnemonic_group)
            number_of_accounts = dpg.add_input_text(parent=mnemonic_group)
            dpg.add_button(label="Ok", width=75,
                           user_data=(modal_id, True, "Import Multiple Accounts", mnemonic_phrase, number_of_accounts),
                           callback=on_selection, parent=alert_message_group)
            dpg.add_button(label="Cancel", width=75, user_data=(modal_id, False, "Import Multiple Accounts"),
                           callback=on_selection, parent=alert_message_group)


def show_import_account_notification(title, message):
    with dpg.mutex():
        with dpg.window(label=title, width=700, height=400, modal=True, no_close=True) as modal_id:
            alert_message_group = dpg.add_group(horizontal=True)
            dpg.add_text(message)
            input_mnemonic_group = dpg.add_group(horizontal=True)
            dpg.add_text("Input mnemonic", pos=(10, 200), parent=input_mnemonic_group)
            mnemonic_phrase = dpg.add_input_text(parent=input_mnemonic_group)
            dpg.add_button(label="Ok", width=75, user_data=(modal_id, True, "Import Account", mnemonic_phrase),
                           callback=on_selection, parent=alert_message_group)
            dpg.add_button(label="Cancel", width=75, user_data=(modal_id, False, "Import Account"),
                           callback=on_selection, parent=alert_message_group)


def show_send_ether_notification(title, message, to, amount):
    with dpg.mutex():

        if to_address:
            with dpg.window(label=title, width=700, height=400, modal=True, no_close=True) as modal_id:
                alert_message_group = dpg.add_group(horizontal=True)
                dpg.add_text(message)
                dpg.add_button(label="Ok", width=75,
                               user_data=(modal_id, True, "Send Ether", to, amount),
                               callback=on_selection, parent=alert_message_group)
                dpg.add_button(label="Cancel", width=75, user_data=(modal_id, False), callback=on_selection,
                               parent=alert_message_group)
        else:
            return


def show_created_account_info(title, decrypt_pub_address, decrypt_private_key, wallet_unlock_key,
                              decrypt_mnemonic_phrase):
    with dpg.mutex():
        with dpg.window(label=title, width=700, height=420):
            account_created_group = dpg.add_group()
            account_unlock_key_warning = dpg.add_group()
            dpg.add_text("Public address", parent=account_created_group)
            account_public_key = dpg.add_input_text(default_value=decrypt_pub_address, width=500,
                                                    parent=account_created_group, no_spaces=True, readonly=True)
            dpg.add_text("Account private key", parent=account_created_group)
            account_private_key = dpg.add_input_text(default_value=decrypt_private_key, width=580,
                                                     parent=account_created_group, no_spaces=True, readonly=True)
            dpg.add_text("Account unlock key", parent=account_created_group)
            wallet_unlock_key = dpg.add_input_text(default_value=wallet_unlock_key, width=510,
                                                   parent=account_created_group, no_spaces=True, readonly=True)
            dpg.add_text("Account mnemonic", parent=account_created_group)
            account_mnemonic = dpg.add_input_text(default_value=decrypt_mnemonic_phrase, width=620,
                                                  parent=account_created_group)
            dpg.add_text("", parent=account_unlock_key_warning)
            dpg.add_text("WARNING: Make sure to save your account unlock key!", parent=account_unlock_key_warning)
            dpg.add_text("This key will not be saved by the Tesseract Client.", parent=account_unlock_key_warning)
            dpg.bind_font(created_account_font)


def show_transfer_token_thelootbox(title, message, nft_contract_address, token_id):
    with dpg.mutex():

        if nft_contract_address:
            with dpg.window(label=title, width=700, height=400, modal=True, no_close=True) as modal_id:
                alert_message_group = dpg.add_group(horizontal=True)
                dpg.add_text(message)
                dpg.add_button(label="Ok", width=75, user_data=(
                    modal_id, True, "Transfer nft TheLootBox", nft_contract_address, token_id), callback=on_selection,
                               parent=alert_message_group)
                dpg.add_button(label="Cancel", width=75, user_data=(modal_id, False), callback=on_selection,
                               parent=alert_message_group)
        else:
            return


def show_thelootbox_bundle_notification(title, message):
    with dpg.mutex():

        if nft_contract_input:
            with dpg.window(label=title, width=700, height=400, modal=True, no_close=True) as modal_id:
                alert_message_group = dpg.add_group(horizontal=True)
                dpg.add_text(message)
                dpg.add_button(label="Ok", width=75, user_data=(modal_id, True, "Create bundle"), callback=on_selection,
                               parent=alert_message_group)
                dpg.add_button(label="Cancel", width=75, user_data=(modal_id, False), callback=on_selection,
                               parent=alert_message_group)
        else:
            return


def show_info(title, message, selection_callback, function_name):
    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()

        with dpg.window(label=title, modal=True, no_close=True) as modal_id:
            if function_name == "Transfer nft":
                alert_message_group = dpg.add_group(horizontal=True)
                dpg.add_text(message)
                dpg.add_button(label="Ok", width=75, user_data=(modal_id, True, function_name),
                               callback=selection_callback, parent=alert_message_group)
                dpg.add_button(label="Cancel", width=75, user_data=(modal_id, False), callback=selection_callback,
                               parent=alert_message_group)
    dpg.split_frame()
    width = dpg.get_item_width(modal_id)
    height = dpg.get_item_height(modal_id)
    dpg.set_item_pos(modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


# --------
# Draw GUI
# --------

with dpg.window(pos=(0, 370), label="Create TheLootBox bundle", width=800, height=600, collapsed=True):
    your_address_group = dpg.add_group(horizontal=True)
    your_address_group_two = dpg.add_group(horizontal=True)
    dpg.add_text("Create a loot bundle by clicking create bundle,", parent=your_address_group)
    dpg.add_text("your current public address will be set as the owner.", parent=your_address_group_two)

    dpg.add_button(pos=(10, 120), label="Create bundle",
                   callback=lambda: show_thelootbox_bundle_notification("Authorization required",
                                                                        "Approve transaction?"))
    dpg.bind_font(default_font)

with dpg.window(pos=(0, 405), label="Transfer ERC721 to TheLootBox weekly giveaway", width=800, height=600,
                collapsed=True):
    input_nft_contract_group = dpg.add_group(horizontal=True)
    dpg.add_text("Input public nft contract address", parent=input_nft_contract_group)
    nft_contract_input = dpg.add_input_text(parent=input_nft_contract_group, no_spaces=True)

    token_id_group = dpg.add_group(horizontal=True)
    dpg.add_text("Input nft id that you own", parent=token_id_group)
    token_id_input = dpg.add_input_text(parent=token_id_group, no_spaces=True)
    wallet_key_input = ""
    dpg.add_button(pos=(10, 110), label="Send NFT to TheLootBox",
                   callback=lambda: show_transfer_token_thelootbox("Authorization required", "Approve transaction?",
                                                                   dpg.get_value(nft_contract_input),
                                                                   dpg.get_value(token_id_input)))
    dpg.bind_font(default_font)

with dpg.window(pos=(0, 335), label="Send Ether", width=800, height=600, collapsed=True):
    to_address_group = dpg.add_group(horizontal=True)
    amount_to_send_group = dpg.add_group(horizontal=True)
    dpg.add_text("To", parent=to_address_group)
    to_address = dpg.add_input_text(parent=to_address_group, no_spaces=True)
    dpg.add_text("Enter amount of Ether to send", parent=amount_to_send_group)
    amount_of_ether = dpg.add_input_text(parent=amount_to_send_group, no_spaces=True)
    dpg.add_button(pos=(10, 120), label="Send Ether",
                   callback=lambda: show_send_ether_notification("Authorization required", "Approve transaction?",
                                                                 on_selection, dpg.get_value(to_address),
                                                                 dpg.get_value(amount_of_ether)))
    dpg.bind_font(default_font)

with dpg.window(pos=(0, 300), label="Account", width=800, height=600, collapsed=True):
    if not os.path.exists("accounts.json"):
        public_address = ""
    else:
        with open('accounts.json', 'r') as accounts:
            account_data = json.load(accounts)
            public_address = account_data[0]['public_address']

    public_address_group = dpg.add_group()
    dpg.add_text("If you have an account set your public address will be displayed here!", parent=public_address_group)
    dpg.add_input_text(default_value=public_address, parent=public_address_group)
    dpg.add_text("Input your account id and password here and click account to view your private key!",
                 parent=public_address_group)
    dpg.add_text("Account Id", parent=public_address_group)
    account_id_input = dpg.add_input_text(parent=public_address_group)
    dpg.add_text("Wallet unlock key", parent=public_address_group)
    wallet_key_input = dpg.add_input_text(parent=public_address_group)
    dpg.add_button(pos=(10, 300), label="Show account info",
                   callback=lambda: show_specific_account(dpg.get_value(account_id_input),
                                                          dpg.get_value(wallet_key_input)))
    dpg.bind_font(default_font)

with dpg.window(label="Create or import account", width=800, height=300) as modal_id:
    with dpg.mutex():
        dpg.add_text("Welcome to the Tesseract client!")
        create_account_group = dpg.add_group()
        dpg.add_button(pos=(10, 100), label="Create account", callback=create_eth_account_callback,
                       parent=create_account_group)
        dpg.add_button(pos=(10, 150), label="Import account from mnemonic",
                       callback=lambda: show_import_account_notification("Import account", "Approve?"),
                       parent=create_account_group)
        dpg.add_button(pos=(10, 200), label="Import multiple accounts from mnemonic",
                       callback=lambda: show_import_multiple_accounts_notification("Import multiple accounts", "Approve?"),
                       parent=create_account_group)

        dpg.bind_font(default_font)

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (92, 184, 92), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (90, 120, 90), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)
dpg.create_viewport(title='Tesseract client', width=800, height=700)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
