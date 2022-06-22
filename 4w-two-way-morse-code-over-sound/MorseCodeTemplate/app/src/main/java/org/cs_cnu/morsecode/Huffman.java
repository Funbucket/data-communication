package org.cs_cnu.morsecode;

import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.PriorityQueue;

class Node {
    int freq;
    char c;

    Node left;
    Node right;
}

class MyCompatrator implements Comparator<Node> {
    public int compare(Node x, Node y) {
        return x.freq - y.freq;
    }
}

public class Huffman {
    static private Map<Character, Integer> frequencies = new HashMap<>();

    public static void printNodes(Node root, String s) {
        if ( root.left == null && root.right == null ) {
            System.out.println(root.c + ":" + s);
            return;
        }
        printNodes(root.left, s + ".");
        printNodes(root.right, s + "-");
    }

    public static String huffmanDecode(String morse, Node root) {
        String decoded = "";
        Node n = root;
        for (int i=0; i < morse.length(); ) {
            Node tmp = n;
            while ( tmp.left != null && tmp.right != null && i < morse.length() ) {
                if ( morse.charAt(i) == '.' ) {
                    tmp = tmp.left;
                } else {
                    tmp = tmp.right;
                }
                i++;
            }
            if ( tmp != null ) {
                decoded += tmp.c;
            }
        }
        return decoded;
    }

    public static Node huffmanEncode() {
        frequencies.put('0', 838945); frequencies.put('F', 534335); frequencies.put( '6', 420780);
        frequencies.put('7', 398565); frequencies.put('E', 375323); frequencies.put('1', 354196);
        frequencies.put('3',351331); frequencies.put('B', 346185); frequencies.put('8', 345643);
        frequencies.put('D', 344459); frequencies.put('2', 344252); frequencies.put('5', 342963);
        frequencies.put('9', 338532); frequencies.put('C', 331465); frequencies.put('4', 328402);
        frequencies.put('A', 314462);

        PriorityQueue<Node> pq = new PriorityQueue<Node>(16, new MyCompatrator());

        Iterator<Character> keys = frequencies.keySet().iterator();

        while( keys.hasNext() ) {
            Node n = new Node();

            char c = keys.next();
            n.c = c;
            n.freq = frequencies.get(c);
            n.left = null;
            n.right = null;

            pq.add(n);
        }

        Node root = null;

        while ( pq.size() > 1 ) {
            Node x = pq.peek();
            pq.poll();

            Node y = pq.peek();
            pq.poll();

            Node f = new Node();

            f.freq = x.freq + y.freq;

            f.right = x;
            f.left = y;

            root = f;
            pq.add(f);
        }

        return root;
    }
}


