class Notifier:
    """
    Base notifier class, handles the connect/disconnect alert wording so
    that concrete notifiers only need to implement send_notification.
    """
    connect_alert = "🐉 Wireguard: {client_name} tunnel is up"
    disconnect_alert = "🐉 Wireguard: {client_name} tunnel potentially seems down"

    def send_notification(self, message):
        """
        Send a notification, to implement in subclasses
        :param message: Message to send
        :return:
        """
        raise NotImplementedError

    def notify_connected(self, client_name):
        """
        Notify connected method to send message connection
        :param client_name: Name of the client to display
        :return:
        """
        self.send_notification(self.connect_alert.format(client_name=client_name))

    def notify_disconnected(self, client_name):
        """
        Notify disconnected method to send message disconnection
        :param client_name: Name of the client to display
        :return:
        """
        self.send_notification(self.disconnect_alert.format(client_name=client_name))
