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

    def repeat_update_or_create(self, pos, old_pos, stock_param):
        for i, position in enumerate(pos):
            for j, old_position in enumerate(old_pos):
                if i == j:
                    StockProduct.objects.update_or_create(stock=stock_param.id,
                                                          product=old_position.product,
                                                          quantity=old_position.quantity,
                                                          price=old_position.price,
                                                          defaults={**position})

    def update(self, instance, validated_data):
        positions = validated_data.pop('positions')
        stock = super().update(instance, validated_data)

        old_positions = instance.positions.all()
        if len(old_positions) == len(positions):
            self.repeat_update_or_create(positions, old_positions, stock)

        elif len(instance.positions.all()) > len(positions):
            differ = len(instance.positions.all()) - len(positions)
            for i in range(differ):
                instance.positions.first().delete()

            old_positions = instance.positions.all()
            self.repeat_update_or_create(positions, old_positions, stock)

        elif len(instance.positions.all()) < len(positions):
            old_positions = instance.positions.all()
            for i, old_position in enumerate(old_positions):
                for j, position in enumerate(positions):
                    for a in range(len(old_positions)):
                        if j == a:
                            StockProduct.objects.update_or_create(stock_id=stock.id,
                                                                  product=old_position.product,
                                                                  quantity=old_position.quantity,
                                                                  price=old_position.price,
                                                                  defaults={**position})
                        if a == len(old_positions) - 1:
                            StockProduct.objects.update_or_create(stock_id=stock.id,
                                                                  product=position['product'],
                                                                  quantity=position['quantity'],
                                                                  price=position['price'])
                break

        return stock
