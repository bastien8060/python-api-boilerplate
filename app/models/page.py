from app.models.response import response_error_generic
from app.models.pages.generic import Model as generic
from app.models.pages.profile import Model as profile
from app.models.pages.posts import Model as posts

class Registry:
    page_mapping = {}

    def register(model) -> None:
        """
        Function to register a page
        """
        Registry.page_mapping[model.name] = model.content

Registry.register(generic)
Registry.register(profile)
Registry.register(posts)

class Page:
    def run(page: str, component: str, payload:dict, authResult: dict) -> str:
        """
        Function to run a page
        """
        try:
            email = authResult.get('email')
            verified = authResult.get('verified')

            ret_obj = Registry.page_mapping[page][component](payload, email, verified)
            if len(ret_obj) == 3:
                return ret_obj
            else:
                return ret_obj, 200, {'Content-Type': 'application/json'}
        except Exception as e:
            print(e)
            return response_error_generic(str(e))