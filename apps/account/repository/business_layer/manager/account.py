class AccountBusinessLogicLayer:
    def is_logged_in(self) -> bool:
        """
        check if the user is logged in
        """
        ...

    def redirect_page(self,
                      page_name: str = None) -> None:
        """
        redirect the user to the specific app and view
        e.g.:
            `pages: account-dashboard` redirects to the login page
        """
        ...

    def log_in(self) -> None:
        """
        provide log in process with the user's phone number and password
        """
        ...

    def sign_up(self) -> None:
        """
        provide sign up process with the user's phone number and password
        """
        ...

    def is_too_many_attempts(self,
                             try_threshold: int = 3) -> bool:
        """
        check if the user has tried more than the specified attempts
        """
        ...

    def block_ip(self,
                 block_time: int = None):
        """
        block IP for the `block_time` period
        """
        ...

    def is_active(self,
                  user: 'User') -> bool:
        """
        Checks whether the user is active.
        """
        return user.is_active
