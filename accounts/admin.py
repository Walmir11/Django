from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Configuração do Admin para o modelo de usuário customizado.
    """
    # Adiciona 'user_type' à lista de campos exibidos na listagem de usuários
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'user_type')

    # Adiciona 'user_type' aos filtros laterais
    list_filter = UserAdmin.list_filter + ('user_type',)

    # Adiciona 'user_type' aos campos editáveis na página de detalhes do usuário
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('user_type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type',)}),
    )