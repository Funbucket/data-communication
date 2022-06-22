class Node:
    def __init__(self, freq, hex_string, left=None, right=None):
        self.freq = freq  # frequency of symbol
        self.hex_string = hex_string
        self.left = left  # left Node
        self.right = right  # right Node
        self.code = ''  # '.' or '-'


# 실습4 apk 파일을 토대로 분석한 빈도수
HEX_FREQ = {
    '0': 838945,
    'F': 534335,
    '6': 420780,
    '7': 398565,
    'E': 375323,
    '1': 354196,
    '3': 351331,
    'B': 346185,
    '8': 345643,
    'D': 344459,
    '2': 344252,
    '5': 342963,
    '9': 338532,
    'C': 331465,
    '4': 328402,
    'A': 314462
}


def huffman_encode():
    hex_strings = HEX_FREQ.keys()

    nodes = []

    for hex in hex_strings:
        nodes.append(Node(HEX_FREQ.get(hex), hex))

    while len(nodes) > 1:
        nodes = sorted(nodes, key=lambda x: x.freq)  # 빈도수를 기준으로 오름차순 정렬

        # 빈도수 가장 작은 노드 2개
        right = nodes[0]
        left = nodes[1]

        left.code = '.'
        right.code = '-'

        # 빈도수 가장 작은 2개 노드 결합해서 부모 노드 생성
        newNode = Node(left.freq + right.freq, left.hex_string + right.hex_string, left, right)

        nodes.remove(left)
        nodes.remove(right)
        nodes.append(newNode)

    return nodes


def huffman_decode(morse, huffman_tree):
    tree_head = huffman_tree
    decoded_output =[]

    for m in morse:
        if m == '.':
            huffman_tree = huffman_tree.left
        elif m == '-':
            huffman_tree = huffman_tree.right
        try:
            if huffman_tree.left.hex_string == None and huffman_tree.right.hex_string == None:
                pass
        except AttributeError:
            decoded_output.append(huffman_tree.hex_string)
            huffman_tree = tree_head

    string = ''.join([str(i) for i in decoded_output])
    return string


def print_nodes(node, val=''):
    # 현재 노드의 code
    new_value = val + str(node.code)

    # recursive case : edge 노드 전까지 recursion
    if (node.left):
        print_nodes(node.left, new_value)
    if (node.right):
        print_nodes(node.right, new_value)

    # base case : edge 노드이면 출력
    if (not node.left and not node.right):
        print(f"{node.hex_string} -> {new_value}")


if __name__ == '__main__':
    huffman_tree = huffman_encode()
    # print_nodes(huffman_tree[0])
