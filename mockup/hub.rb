Shoes.app do
  background white
  stack do
    border black
    para "Hub name", :align => 'center'
    edit_line :text => "Search!"
    flow do
      stack :width => -150 do
        border black
        para "Notifications"
      end
      stack :width => 150 do
        border black
        para "Users"
      end
    end
    para "Chat"
  end
end
