Shoes.app do
  stack do
    para "Hub name", :align => 'center'
    edit_line :text => "Search!"
    flow do
      stack :width => -100 do
        para "Notifications"
      end
      stack :width => 100 do
        para "Users"
      end
    end
    para "Chat"
  end
end
