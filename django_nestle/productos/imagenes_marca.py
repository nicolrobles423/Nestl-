# Foto real por producto específico (con licencia libre, tomada de Wikimedia
# Commons). Solo cubro los productos para los que encontré una foto real y
# verificable; el resto queda sin imagen a propósito.
IMAGEN_POR_PRODUCTO = {
    'Nestlé Crunch Pack 4x20g': 'productos/nestle_crunch_barra.jpg',
    'Kit Kat Chocolate con Leche 41.5g': 'productos/kitkat_barra.jpg',

    'Milo Activ-Go en Polvo 1kg': 'productos/milo_activgo_1kg.jpeg',
    'Milo Activ-Go en Polvo 400g': 'productos/milo_activgo_400g.jpeg',
    'Milo Activ-Go en Polvo 200g': 'productos/milo_activgo_200g.jpeg',
    'Cereal en Bolitas de Chocolate Milo 250g': 'productos/milo_bolas_chocolate_250g.jpeg',
    'Cereal en Bolitas de Chocolate Milo 500g': 'productos/milo_bolas_chocolate_500g.jpeg',
    'Milo Galleta Dulce de Chocolate x12': 'productos/milo_galleta_dulce_chocolate_x12.jpeg',
    'Milo Listo para Tomar 185ml': 'productos/milo_listo_para_tomar_185ml.jpeg',

    'Amor Clásica 100g': 'productos/amor_clasica_100g.png',
    'Amor Clásica 130g': 'productos/amor_clasica_130g.png',
    'Amor Clásica 175g': 'productos/amor_clasica_175g.png',
    'Amor Doble Crema Doble Sabor Chocolate Fresa 130g': 'productos/amor_doble_chocolate_fresa_130g.png',
    'Amor Doble Crema Doble Sabor Coco Limón 130g': 'productos/amor_doble_coco_limon_130g.jpeg',
    'Amor Doble Crema Doble Sabor Leche Chocolate 130g': 'productos/amor_doble_leche_chocolate_130g.png',
    'Amor Fresa 100g': 'productos/amor_fresa_100g.jpg',
    'Amor Fresa 130g': 'productos/amor_fresa_130g.png',
    'Amor Fresa 175g': 'productos/amor_fresa_175g.jpeg',
    'Amor Limón 100g': 'productos/amor_limon_100g.png',
    'Amor Limón 175g': 'productos/amor_limon_175g.jpg',
    'Amor Naranja 100g': 'productos/amor_naranja_100g.jpeg',
    'Amor Naranja 130g': 'productos/amor_naranja_130g.png',
    'Amor Naranja 175g': 'productos/amor_naranja_175g.jpg',
    'Amor Doble Crema Doble Sabor Coco Limón 100g': 'productos/amor_doble_coco_limon_100g.jpeg',

    'Nescafé 3en1 Caja 184g': 'productos/nescafe_3en1_caja_184g.jpeg',
    'Nescafé Descafeinado Frasco 40g': 'productos/nescafe_descafeinado_40g.jpeg',
    'Nescafé Diario Frasco 50g': 'productos/nescafe_diario_50g.jpeg',
    'Nescafé Dolce Gusto Café Au Lait x16': 'productos/nescafe_dolce_gusto_cafe_au_lait.jpeg',
    'Nescafé Dolce Gusto Cappuccino x16': 'productos/nescafe_dolce_gusto_cappuccino.jpeg',
    'Nescafé Dolce Gusto Chai Tea Latte x16': 'productos/nescafe_dolce_gusto_chai_tea_latte.jpeg',
    'Nescafé Dolce Gusto Edición Kit Kat x10': 'productos/nescafe_dolce_gusto_edicion_kitkat.jpeg',

    'Maggi Adobo Completo La Sazón 200g': 'productos/maggi_adobo_completo_la_sazon_200g.webp',
    'Maggi Caldo de Gallina Doble Gusto en Cubos 80g': 'productos/maggi_caldo_gallina_cubos_80g.jpg',
    'Maggi Caldo en Polvo Sabor a Gallina 69,60g': 'productos/maggi_caldo_polvo_gallina.jpg',

    'La Lechera Crema de Leche UHT 946ml': 'productos/lalechera_crema_leche_946ml.jpg',
    'La Lechera Leche Condensada 100g': 'productos/lalechera_leche_condensada_100g.webp',

    'Kit Kat Chocolate Blanco 41.5g': 'productos/kitkat_blanco_41.5g.jpg',
    'Kit Kat Chocolate Dark 70% Cacao 41.5g': 'productos/kitkat_dark_70_41.5g.webp',
}


def imagen_para_producto(producto):
    """Le asigno la foto real del producto si existe una específica.

    Si no hay una foto verificada para ese producto exacto, devuelvo None
    (no invento ni relleno con una foto genérica de la marca).
    """
    return IMAGEN_POR_PRODUCTO.get(producto.get('name'))
