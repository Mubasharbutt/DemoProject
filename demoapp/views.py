from rest_framework import generics,status
from rest_framework.response import Response
from .models import CartItem, Order ,Item
from .serializers import CartItemSerializer, OrderSerializer
from .serializers import ItemSerializer
from rest_framework.views import APIView
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
#here is api to add items where we check if status is pending then save in cart and if status is accepted then save item in Ordered
class AddItemView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        item_name = data.get('name')
        item_price = data.get('price')
        item_status = data.get('status')

        if item_status == 'Pending':
            item = Item.objects.create(name=item_name, price=item_price, status=item_status)
            cart_item = CartItem.objects.create(item=item)
            item_serializer = ItemSerializer(item)
            cart_item_serializer = CartItemSerializer(cart_item)
            return Response({'item': item_serializer.data, 'cart_item': cart_item_serializer.data}, status=status.HTTP_201_CREATED)
        elif item_status == 'Accepted':
            item = Item.objects.create(name=item_name, price=item_price, status=item_status)
            order = Order.objects.create(total_amount=item_price, is_paid=False)
            order.items.add(item)
            item_serializer = ItemSerializer(item)
            order_serializer = OrderSerializer(order)
            return Response({'item': item_serializer.data, 'order': order_serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid item status'}, status=status.HTTP_400_BAD_REQUEST)
        
#API TO SHOW all orders
class OrderListAPI(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

#api to sjow all orders by id
class OrderDetailAPI(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
#ApI To show all items from cart and ordered and to show total fee      
class AllItemsView(APIView):
    def get(self, request):
        try:
            cart_items = CartItem.objects.all()
            order_items = Order.objects.filter(is_paid=False).values_list('items__id', flat=True)
            all_items = Item.objects.filter(id__in=list(cart_items.values_list('item__id', flat=True)) + list(order_items))
            total_fee = sum(all_items.values_list('price', flat=True), Decimal(0))
            serializer = ItemSerializer(all_items, many=True)
            return Response({
                'items': serializer.data,
                'total_fee': total_fee
            })
        except ObjectDoesNotExist:
            return Response({'error': 'One or more objects does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Api to make payment 
class PaymentView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if not order.is_paid:
                # Here we can add the payment logic
                order.is_paid = True
                order.save()
                
                return Response({'message': 'Payment successful. Order is now paid.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Order is already paid.'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
