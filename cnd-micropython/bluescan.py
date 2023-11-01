    # Works - see https://docs.micropython.org/en/latest/library/bluetooth.html

import ubluetooth
import time
from micropython import const
import machine

def bluescan():

    led = machine.Pin(2, machine.Pin.OUT)

    _IRQ_CENTRAL_CONNECT = const(1)
    _IRQ_CENTRAL_DISCONNECT = const(2)
    _IRQ_GATTS_WRITE = const(3)
    _IRQ_GATTS_READ_REQUEST = const(4)
    _IRQ_SCAN_RESULT = const(5)
    _IRQ_SCAN_DONE = const(6)
    _IRQ_PERIPHERAL_CONNECT = const(7)
    _IRQ_PERIPHERAL_DISCONNECT = const(8)
    _IRQ_GATTC_SERVICE_RESULT = const(9)
    _IRQ_GATTC_SERVICE_DONE = const(10)
    _IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
    _IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
    _IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
    _IRQ_GATTC_DESCRIPTOR_DONE = const(14)
    _IRQ_GATTC_READ_RESULT = const(15)
    _IRQ_GATTC_READ_DONE = const(16)
    _IRQ_GATTC_WRITE_DONE = const(17)
    _IRQ_GATTC_NOTIFY = const(18)
    _IRQ_GATTC_INDICATE = const(19)
    _IRQ_GATTS_INDICATE_DONE = const(20)
    _IRQ_MTU_EXCHANGED = const(21)
    _IRQ_L2CAP_ACCEPT = const(22)
    _IRQ_L2CAP_CONNECT = const(23)
    _IRQ_L2CAP_DISCONNECT = const(24)
    _IRQ_L2CAP_RECV = const(25)
    _IRQ_L2CAP_SEND_READY = const(26)
    _IRQ_CONNECTION_UPDATE = const(27)
    _IRQ_ENCRYPTION_UPDATE = const(28)
    _IRQ_GET_SECRET = const(29)
    _IRQ_SET_SECRET = const(30)



    def bt_irq(event, data):
        print("e=",end="")
        #print(bytes(event), end="")
        print(event, end="")
        #print(" d=",end="")
        #print(data)
        #led.value(1)
        #time.sleep(1)
        #led.value(0)
        #time.sleep(1)

        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" addr_type=",end="")
            print(addr_type,end="")
            print(" addr=",end="")
            print(bytes(addr),end="")
            print("# A central has connected to this peripheral.")

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" addr_type=",end="")
            print(addr_type,end="")
            print(" addr=",end="")
            print(bytes(addr),end="")
            print("# A central has disconnected from this peripheral.")

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, attr_handle = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" attr_handle=",end="")
            print(attr_handle,end="")
            print("# A client has written to this characteristic or descriptor.")

        elif event == _IRQ_GATTS_READ_REQUEST:
            conn_handle, attr_handle = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" attr_handle=",end="")
            print(attr_handle,end="")
            print("# A client has issued a read. Note: this is only supported on STM32.  # Return a non-zero integer to deny the read (see below), or zero (or None) # to accept the read.")
            _GATTS_NO_ERROR = const(0x00)
            _GATTS_ERROR_READ_NOT_PERMITTED = const(0x02)
            _GATTS_ERROR_WRITE_NOT_PERMITTED = const(0x03)
            _GATTS_ERROR_INSUFFICIENT_AUTHENTICATION = const(0x05)
            _GATTS_ERROR_INSUFFICIENT_AUTHORIZATION = const(0x08)
            _GATTS_ERROR_INSUFFICIENT_ENCRYPTION = const(0x0f)

        elif event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            print(" addr_type=",end="")
            print(addr_type,end="")
            print(" addr=",end="")
            print(bytes(addr),end="")
            print(" adv_type=",end="")
            print(adv_type,end="")
            #
            # 0x00 - ADV_IND - connectable and scannable undirected advertising
            # 0x01 - ADV_DIRECT_IND - connectable directed advertising
            # 0x02 - ADV_SCAN_IND - scannable undirected advertising
            # 0x03 - ADV_NONCONN_IND - non-connectable undirected advertising
            # 0x04 - SCAN_RSP - scan response
            #
            print(" rssi=",end="")
            print(rssi,end="")
            print(" adv_data=",end="")
            print(bytes(adv_data),end="")
            print("# A single scan result.")

        elif event == _IRQ_SCAN_DONE:
            print("# Scan duration finished or manually stopped.")
            pass
        
        elif event == _IRQ_PERIPHERAL_CONNECT:
            conn_handle, addr_type, addr = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" addr_type=",end="")
            print(addr_type,end="")
            print(" addr=",end="")
            print(bytes(addr),end="")
            print("# A successful gap_connect().")

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" addr_type=",end="")
            print(addr_type,end="")
            print(" addr=",end="")
            print(bytes(addr),end="")
            print("# Connected peripheral has disconnected.")

        elif event == _IRQ_GATTC_SERVICE_RESULT:
            conn_handle, start_handle, end_handle, uuid = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" start_handle=",end="")
            print(start_handle,end="")
            print(" end_handle=",end="")
            print(end_handle,end="")
            print(" uuid=",end="")
            print(bluetooth.UUID(uuid),end="")
            print("# Called for each service found by gattc_discover_services().")

        elif event == _IRQ_GATTC_SERVICE_DONE:
            conn_handle, status = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" status=",end="")
            print(status,end="")
            print("# Called once service discovery is complete.  # Note: Status will be zero on success, implementation-specific value otherwise.")

        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            conn_handle, end_handle, value_handle, properties, uuid = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" end_handle=",end="")
            print(end_handle,end="")
            print(" value_handle=",end="")
            print(value_handle,end="")
            print(" properties=",end="")
            print(properties,end="")
            print(" uuid=",end="")
            print(bluetooth.UUID(uuid),end="")
            print("# Called for each characteristic found by gattc_discover_services().")

        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            conn_handle, status = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" status=",end="")
            print(status,end="")
            print("# Called once service discovery is complete.  # Note: Status will be zero on success, implementation-specific value otherwise.")

        elif event == _IRQ_GATTC_DESCRIPTOR_RESULT:
            conn_handle, dsc_handle, uuid = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" dsc_handle=",end="")
            print(dsc_handle,end="")
            print(" uuid=",end="")
            print(bluetooth.UUID(uuid),end="")
            print("# Called for each descriptor found by gattc_discover_descriptors().")

        elif event == _IRQ_GATTC_DESCRIPTOR_DONE:
            conn_handle, status = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" status=",end="")
            print(status,end="")
            print("# Called once service discovery is complete.  # Note: Status will be zero on success, implementation-specific value otherwise.")

        elif event == _IRQ_GATTC_READ_RESULT:
            conn_handle, value_handle, char_data = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" value_handle=",end="")
            print(value_handle,end="")
            print(" char_data=",end="")
            print(bytes(char_data),end="")
            print("# A gattc_read() has completed.")

        elif event == _IRQ_GATTC_READ_DONE:
            conn_handle, value_handle, status = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" value_handle=",end="")
            print(value_handle,end="")
            print(" status=",end="")
            print(status,end="")
            print("# A gattc_read() has completed.  # Note: Status will be zero on success, implementation-specific value otherwise.")

        elif event == _IRQ_GATTC_WRITE_DONE:
            conn_handle, value_handle, status = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" value_handle=",end="")
            print(value_handle,end="")
            print(" status=",end="")
            print(status,end="")
            print("# A gattc_write() has completed.  # Note: Status will be zero on success, implementation-specific value otherwise.")

        elif event == _IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" value_handle=",end="")
            print(value_handle,end="")
            print(" notify_data=",end="")
            print(bytes(notify_data),end="")
            print("# A server has sent a notify request.")

        elif event == _IRQ_GATTC_INDICATE:
            conn_handle, value_handle, notify_data = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" value_handle=",end="")
            print(value_handle,end="")
            print(" notify_data=",end="")
            print(bytes(notify_data),end="")
            print("# A server has sent an indicate request.")

        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" value_handle=",end="")
            print(value_handle,end="")
            print(" status=",end="")
            print(status,end="")
            print("# A client has acknowledged the indication.  # Note: Status will be zero on successful acknowledgment, implementation-specific value otherwise.")

        elif event == _IRQ_MTU_EXCHANGED:
            conn_handle, mtu = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" mtu=",end="")
            print(mtu,end="")
            print("# ATT MTU exchange complete (either initiated by us or the remote device).")

        elif event == _IRQ_L2CAP_ACCEPT:
            conn_handle, cid, psm, our_mtu, peer_mtu = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" cid=",end="")
            print(cid,end="")
            print(" psm=",end="")
            print(psm,end="")
            print(" our_mtu=",end="")
            print(our_mtu,end="")
            print(" peer_mtu=",end="")
            print(peer_mtu,end="")
            print("# A new channel has been accepted.  # Return a non-zero integer to reject the connection, or zero (or None) to accept.")

        elif event == _IRQ_L2CAP_CONNECT:
            conn_handle, cid, psm, our_mtu, peer_mtu = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" cid=",end="")
            print(cid,end="")
            print(" psm=",end="")
            print(psm,end="")
            print(" our_mtu=",end="")
            print(our_mtu,end="")
            print(" peer_mtu=",end="")
            print(peer_mtu,end="")
            print("# A new channel is now connected (either as a result of connecting or accepting).")

        elif event == _IRQ_L2CAP_DISCONNECT:
            conn_handle, cid, psm, status = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" cid=",end="")
            print(cid,end="")
            print(" psm=",end="")
            print(psm,end="")
            print(" status=",end="")
            print(status,end="")
            print("# Existing channel has disconnected (status is zero), or a connection attempt failed (non-zero status).")

        elif event == _IRQ_L2CAP_RECV:
            conn_handle, cid = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" cid=",end="")
            print(cid,end="")
            print("# New data is available on the channel. Use l2cap_recvinto to read.")

        elif event == _IRQ_L2CAP_SEND_READY:
            conn_handle, cid, status = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" cid=",end="")
            print(cid,end="")
            print(" status=",end="")
            print(status,end="")
            print("# A previous l2cap_send that returned False has now completed and the channel is ready to send again.  # If status is non-zero, then the transmit buffer overflowed and the application should re-send the data.")

        elif event == _IRQ_CONNECTION_UPDATE:
            conn_handle, conn_interval, conn_latency, supervision_timeout, status = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" conn_interval=",end="")
            print(conn_interval,end="")
            print(" conn_latency=",end="")
            print(conn_latency,end="")
            print(" supervision_timeout=",end="")
            print(supervision_timeout,end="")
            print(" status=",end="")
            print(status,end="")
            print("# The remote device has updated connection parameters.")

        elif event == _IRQ_ENCRYPTION_UPDATE:
            conn_handle, encrypted, authenticated, bonded, key_size = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" encrypted=",end="")
            print(encrypted,end="")
            print(" authenticated=",end="")
            print(authenticated,end="")
            print(" bonded=",end="")
            print(bonded,end="")
            print(" key_size=",end="")
            print(key_size,end="")
            print("# The encryption state has changed (likely as a result of pairing or bonding).")

        elif event == _IRQ_GET_SECRET:
            sec_type, index, key = data
            print(" sec_type=",end="")
            print(sec_type,end="")
            print(" index=",end="")
            print(index,end="")
            print(" key=",end="")
            print(key,end="")

            print("# Return a stored secret.  # If key is None, return the index'th value of this sec_type.  # Otherwise return the corresponding value for this sec_type and key.")
            return 123 #// value
        elif event == _IRQ_SET_SECRET:
            sec_type, key, value = data
            print(" sec_type=",end="")
            print(sec_type,end="")
            print(" key=",end="")
            print(key,end="")
            print(" value=",end="")
            print(value,end="")

            print("# Save a secret to the store for this sec_type and key.")
            return True
        elif event == _IRQ_PASSKEY_ACTION:
            conn_handle, action, passkey = data
            print(" conn_handle=",end="")
            print(conn_handle,end="")
            print(" action=",end="")
            print(action,end="")
            print(" passkey=",end="")
            print(passkey,end="")
            print("# Respond to a passkey request during pairing.  # See gap_passkey() for details.  # action will be an action that is compatible with the configured 'io' config.  # passkey will be non-zero if action is 'numeric comparison'.")
            _PASSKEY_ACTION_NONE = const(0)
            _PASSKEY_ACTION_INPUT = const(2)
            _PASSKEY_ACTION_DISPLAY = const(3)
            _PASSKEY_ACTION_NUMERIC_COMPARISON = const(4)

        else:
            print(" unknown event")




    print('hi')
    ble = ubluetooth.BLE()
    ble.active(True)
    ble.irq(bt_irq)
    addr_type, addr = ble.config('mac')
    print("my addr_type=",end="")
    print(addr_type,end="")
    print(" addr=",end="")
    print(bytes(addr))
    print("my gap_name=",end="")
    print(ble.config(gap_name='ESP32mpyD1F'))

    #print("my rxbuf=",end="")
    #print(ble.config(rxbuf))

    _IO_CAPABILITY_DISPLAY_ONLY = const(0)
    _IO_CAPABILITY_DISPLAY_YESNO = const(1)
    _IO_CAPABILITY_KEYBOARD_ONLY = const(2)
    _IO_CAPABILITY_NO_INPUT_OUTPUT = const(3)
    _IO_CAPABILITY_KEYBOARD_DISPLAY = const(4)

    ble.config(io=_IO_CAPABILITY_NO_INPUT_OUTPUT)

    print('advertising for a bit...')

    #BLE.gap_advertise(interval_us, adv_data=None, *, resp_data=None, connectable=True)
    ble.gap_advertise(1280000, adv_data="HelloESP32", resp_data="Gotme", connectable=True)
    time.sleep(20)
    ble.gap_advertise(None)
    print('stopped advertising. Start scanning')


    #ble.gap_scan(10000)
    #BLE.gap_scan(duration_ms, interval_us=1280000, window_us=11250, active=False, /)

    ble.gap_scan(10000, 10000, 10000, True)
    print('over2')
    time.sleep(20)
    print('over3')




