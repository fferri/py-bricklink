'''
    bricklink.methods
    --------------------

    A module providing Bricklink API Method implementations
'''


from .exceptions import BricklinkInvalidParameterException


class Method:
    client = None

    def __init__(self, client):
        self.client = client


class Orders(Method):
    def getOrders(self, direction='in', status='', filed=False):
        return self.client.get('/orders', {'direction': direction, 'status': status, 'filed': filed})

    def getOrder(self, order_id):
        return self.client.get('/orders/%d' % order_id)

    def getOrderItems(self, order_id):
        return self.client.get('/orders/%d/items' % order_id)

    def getOrderMessages(self, order_id):
        return self.client.get('/orders/%d/messages' % order_id)

    def getOrderFeedback(self, order_id):
        return self.client.get('/orders/%d/feedback' % order_id)

    def updateOrder(self, order_id, **kwargs):
        return self.client.put('/orders/%d' % order_id, kwargs)

    def updateOrderStatus(self, order_id, order_status):
        return self.client.put('/orders/%d/status' % order_id, {'field': 'status', 'value': order_status})

    def updatePaymentStatus(self, order_id, payment_status):
        return self.client.put('/orders/%d/status' % order_id, {'field': 'payment_status', 'value': payment_status})

    def sendDriveThru(self, order_id, mail_me):
        return self.client.put('/orders/%d/drive_thru' % order_id, {'mail_me': bool(mail_me)})


class Inventory(Method):
    def getInventories(self, item_type='', status='', category_id='', color_id=''):
        return self.client.get('/inventories', {'item_type': item_type, 'status': status, 'category_id': category_id, 'color_id': color_id})

    def getInventory(self, inventory_id):
        return self.client.get('/inventories/%d' % inventory_id)

    def createInventory(self, **kwargs):
        return self.client.post('/inventories', kwargs)

    def createInventories(self, **kwargs):
        return self.client.post('/inventories', kwargs)

    def updateInventory(self, inventory_id, **kwargs):
        return self.client.post('/inventories/%d' % inventory_id, kwargs)

    def deleteInventory(self, inventory_id):
        return self.client.delete('/inventories/%d' % inventory_id)


class Catalog(Method):
    def getItem(self, type, no):
        return self.client.get('/items/%s/%s' % (type, no))

    def getItemImage(self, type, no, color_id):
        return self.client.get('/items/%s/%s/images/%d' % (type, no, color_id))

    def getSupersets(self, type, no, color_id=''):
        return self.client.get('/items/%s/%s/supersets' % (type, no), {'color_id': color_id})

    def getSubsets(self, type, no, color_id='', box=False, instruction=False, break_minifigs=False, break_subsets=False):
        return self.client.get('/items/%s/%s/subsets' % (type, no), {'color_id': color_id, 'box': box, 'instruction': instruction, 'break_minifigs': break_minifigs, 'break_subsets': break_subsets})

    def getPriceGuide(self, type, no, color_id='', guide_type='stock', new_or_used='N', country_code='', region='', currency_code='', vat='N'):
        return self.client.get('/items/%s/%s/price' % (type, no), {'color_id': color_id, 'guide_type': guide_type, 'new_or_used': new_or_used, 'country_code': country_code, 'region': region, 'currency_code': currency_code, 'vat': vat})

    def getKnownColors(self, type, no):
        return self.client.get('/items/%s/%s/colors' % (type, no))


class Feedback(Method):
    URL_FEEDBACK_LIST = 'feedback'
    URL_FEEDBACK_DETAILS = 'feedback/{feedback_id}'
    URL_FEEDBACK_CREATE = 'feedback'
    URL_FEEDBACK_REPLY = 'feedback/{feedback_id}/reply'


class Color(Method):
    URL_COLOR_LIST = 'colors'
    URL_COLOR_DETAIL = 'colors/{color_id}'


class Category(Method):
    URL_CATEGORY_LIST = 'categories'
    URL_CATEGORY_DETAIL = 'categories/{category_id}'


class PushNotification(Method):
    URL_NOTIFICATION_LIST = 'notifications'
