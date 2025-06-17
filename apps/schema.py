import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from apps.models import User, DeployedApp
from graphql import GraphQLError
import base64
from graphene_django.views import GraphQLView
from django.conf import settings
from apps.dataloaders import UserLoader, AppLoader, UserAppsLoader


# Utility functions for encoding/decoding custom IDs
def encode_relay_id(type_name: str, db_id: str) -> str:
    """
    Encode a database ID and type name into a Relay-compliant global ID.

    Args:
        type_name (str): The GraphQL type name.
        db_id (str): The database ID.
    Returns:
        str: Base64-encoded global ID.
    """
    raw = f"{type_name}:{db_id}"
    return base64.b64encode(raw.encode()).decode()


def decode_relay_id(global_id: str):
    """
    Decode a Relay global ID into its type name and database ID.

    Args:
        global_id (str): The Relay global ID.
    Returns:
        Tuple[str, str]: (type_name, db_id)
    Raises:
        GraphQLError: If the ID format is invalid.
    """
    try:
        decoded = base64.b64decode(global_id).decode()
        type_name, db_id = decoded.split(":", 1)
        return type_name, db_id
    except Exception:
        raise GraphQLError("Invalid global ID format.")


class UserNode(DjangoObjectType):
    """
    GraphQL Node for the User model.
    Implements Relay Node interface and exposes user fields and related apps.
    """

    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = ("id", "username", "plan", "created_at", "updated_at", "apps")

    def resolve_apps(self, info):
        """
        Batch-load all apps for this user using UserAppsLoader to prevent N+1 queries.

        Args:
            info: GraphQL resolve info context.

        Returns:
            List[DeployedApp]: List of apps owned by this user.
        """
        loader = UserAppsLoader()
        # Reason: Efficiently batch loads all apps for a set of users in one query.
        return loader.load_many([self.id])[0]


class DeployedAppNode(DjangoObjectType):
    """
    GraphQL Node for the DeployedApp model.
    Implements Relay Node interface and exposes app fields and owner.
    """

    class Meta:
        model = DeployedApp
        interfaces = (relay.Node,)
        fields = ("id", "active", "owner", "created_at", "updated_at")


class Query(graphene.ObjectType):
    """
    Root GraphQL query object.
    Provides access to all users, all apps, and Relay node lookup.
    """

    node = relay.Node.Field(
        description="Relay Node interface for fetching any object by global ID."
    )
    all_users = graphene.List(UserNode, description="List all users in the system.")
    all_apps = graphene.List(DeployedAppNode, description="List all deployed applications.")

    def resolve_all_users(root, info):
        return User.objects.all()

    def resolve_all_apps(root, info):
        return DeployedApp.objects.all()

    def resolve_node(self, info, id):
        try:
            type_name, db_id = decode_relay_id(id)
            if type_name == "UserNode" and db_id.startswith("u_"):
                return UserNode.get_node(info, db_id)
            elif type_name == "DeployedAppNode" and db_id.startswith("app_"):
                return DeployedAppNode.get_node(info, db_id)
            else:
                raise GraphQLError("ID format does not match any known type.")
        except Exception as e:
            raise GraphQLError(f"Invalid node ID: {e}")

    def resolve_user_apps(self, info, **kwargs):
        user_ids = kwargs.get("user_ids", [])
        loader = UserAppsLoader()
        return loader.load_many(user_ids)


class UpgradeAccount(graphene.Mutation):
    """
    Mutation to upgrade a user's plan to PRO.
    Returns the updated user and success status.
    """

    class Arguments:
        user_id = graphene.ID(required=True)

    user = graphene.Field(lambda: UserNode)
    ok = graphene.Boolean()

    def mutate(self, info, user_id):
        type_name, db_id = decode_relay_id(user_id)
        if type_name != "UserNode":
            raise GraphQLError("Invalid user ID type.")
        user = User.objects.filter(id=db_id).first()
        if not user:
            raise GraphQLError("User not found.")
        if user.plan == "PRO":
            raise GraphQLError("User is already PRO.")
        user.plan = "PRO"
        user.save()
        return UpgradeAccount(user=user, ok=True)


class DowngradeAccount(graphene.Mutation):
    """
    Mutation to downgrade a user's plan to HOBBY.
    Returns the updated user and success status.
    """

    class Arguments:
        user_id = graphene.ID(required=True)

    user = graphene.Field(lambda: UserNode)
    ok = graphene.Boolean()

    def mutate(self, info, user_id):
        type_name, db_id = decode_relay_id(user_id)
        if type_name != "UserNode":
            raise GraphQLError("Invalid user ID type.")
        user = User.objects.filter(id=db_id).first()
        if not user:
            raise GraphQLError("User not found.")
        if user.plan == "HOBBY":
            raise GraphQLError("User is already HOBBY.")
        user.plan = "HOBBY"
        user.save()
        return DowngradeAccount(user=user, ok=True)


class Mutation(graphene.ObjectType):
    """
    Root GraphQL mutation object.
    Provides account upgrade and downgrade mutations.
    """

    upgrade_account = UpgradeAccount.Field(description="Upgrade a user's plan to PRO.")
    downgrade_account = DowngradeAccount.Field(description="Downgrade a user's plan to HOBBY.")


# Add a custom GraphQLView with a simple query complexity limit
class LimitedComplexityGraphQLView(GraphQLView):
    def execute_graphql_request(self, *args, **kwargs):
        document = args[0]
        # Simple limit: max 10 fields per query
        if document and hasattr(document, "definitions"):
            field_count = 0
            for op in document.definitions:
                if hasattr(op, "selection_set") and op.selection_set:
                    field_count += len(op.selection_set.selections)
            if field_count > 10:
                from graphql import GraphQLError

                return None, [
                    GraphQLError("Query too complex: too many fields requested.")
                ]
        return super().execute_graphql_request(*args, **kwargs)


# Instruct user to update urls.py to use LimitedComplexityGraphQLView if needed
# Example:
# from apps.schema import LimitedComplexityGraphQLView
# path('graphql/', csrf_exempt(LimitedComplexityGraphQLView.as_view(graphiql=True))),


schema = graphene.Schema(query=Query, mutation=Mutation)
