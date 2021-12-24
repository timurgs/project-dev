from rest_framework import serializers

from logistic.models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = '__all__'

    def create(self, validated_data):
        positions = validated_data.pop('positions')
        stock = super().create(validated_data)
        for position in positions:
            StockProduct.objects.create(stock_id=stock.id,
                                        product=position['product'],
                                        quantity=position['quantity'],
                                        price=position['price'])
        return stock

    def update(self, instance, validated_data):
        positions = validated_data.pop('positions')
        stock = super().update(instance, validated_data)
        old_positions = instance.positions.all()
        for i, position in enumerate(positions):
            for j, old_position in enumerate(old_positions):
                if i == j:
                    StockProduct.objects.update_or_create(stock=stock.id,
                                                          product=old_position.product,
                                                          quantity=old_position.quantity,
                                                          price=old_position.price,
                                                          defaults={**position})
                if len(positions) > len(old_positions) and len(positions) - len(old_positions) == j + 1:
                    StockProduct.objects.update_or_create(stock_id=stock.id,
                                                          product=position['product'],
                                                          quantity=position['quantity'],
                                                          price=position['price'])
                elif len(positions) < len(old_positions) and len(old_positions) - len(positions) == i + 1:
                    differ = len(instance.positions.all()) - len(positions)
                    for count in range(differ):
                        instance.positions.last().delete()

        return stock
