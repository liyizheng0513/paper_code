#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 00:23:04 2017

@author: liyizheng
"""

class Node(object):
    def __init__(self, val, p=0):
        self.data = val
        self.next = p
        self.prev = p

    def __lt__(self, other):
        if self.data<other.data:
            return True
        else:
            return False


class LinkList(object):
    def __init__(self):
        self.head = 0

    def __getitem__(self, key):
        if self.is_empty():
            print 'linklist is empty.'
            return
        elif key < 0 or key > self.getlength():
            print 'the given key is error'
            return
        else:
            return self.getitem(key)

    def __setitem__(self, key, value):
        if self.is_empty():
            print 'linklist is empty.'
            return
        elif key < 0 or key > self.getlength():
            print 'the given key is error'
            return
        else:
            self.delete(key)
            return self.insert(key)

    def initlist(self, data):
        self.head = Node(data[0])
        p = self.head
        for i in data[1:]:
            node = Node(i)
            p.next = node
            node.prev = p
            p = p.next

    def getlength(self):
        p = self.head
        length = 0
        while p != 0:
            length += 1
            p = p.next
        return length

    def is_empty(self):
        if self.getlength() == 0:
            return True
        else:
            return False

    def clear(self):
        self.head = 0

    def append(self, item):
        q = Node(item)
        if self.head == 0:
            self.head = q
        else:
            p = self.head
            while p.next != 0:
                p = p.next
            p.next = q
            q.prev = p

    def getitem(self, index):
        if self.is_empty():
            print 'Linklist is empty.'
            return
        j = 0
        p = self.head
        while p.next != 0 and j < index:
            p = p.next
            j += 1
        if j == index:
            return p.data
        else:
            print 'target is not exist!'

    def insert(self, index, item):
        if self.is_empty() or index < 0 or index > self.getlength():
            print 'Linklist is empty.'
            return
        if index == 0:
            q = Node(item, self.head)
            self.head = q
        p = self.head
        post = self.head
        j = 0
        while p.next != 0 and j < index:
            post = p
            p = p.next
            j += 1
        if index == j:
            q = Node(item, p)
            post.next = q
            q.prev = post
            q.next = p
            p.prev = q

    def delete_index(self, index):
        if self.is_empty() or index < 0 or index > self.getlength():
            print 'Linklist is empty.'
            return
        if index == 0:
            self.head=self.head.next
            self.head.prev=0

        p = self.head
        post = self.head
        j = 0
        while p.next != 0 and j < index:
            post = p
            p = p.next
            j += 1
        if index == j and j>0:
            post.next = p.next
            if j<self.getlength()-1:
                p.next.prev = post

    def index(self, value):
        if self.is_empty():
            print 'Linklist is empty.'
            return
        p = self.head
        i = 0
        while p.next != 0 and not p.data == value:
            p = p.next
            i += 1
        if p.data == value:
            return i
        else:
            return -1

    def delete(self,g):
        index=self.index(g.data)
        if index==-1:
            print "data is not in List "
        else:
            self.delete_index(index)